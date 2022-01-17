from typing import List


class ClassesExtractor:
    def __init__(self, parsed_classes, parsed_functions):
        self.classes = parsed_classes
        self.functions = parsed_functions

    def collect_data(self) -> List[dict]:
        """
        Tries to parse (via `py:parsepy.Parser`) the classes in the module at module_path, and save the extracted results
        in collected_data.
        If parsing does not succeed an empty list is saved instead
        """
        class_data = list()

        for class_element in self.classes.get("classes", list()):
            class_model = dict()

            class_model["name"] = class_element.get("name", "")
            class_model["start_line"], class_model["end_line"] = (
                class_element.get("start_line"),
                class_element.get("end_line"),
            )
            class_model["total_lines"] = (
                class_model["end_line"] - class_model["start_line"] + 1
            )

            class_model["methods"] = self.collect_class_methods(
                class_model.get("name", ""), self.functions
            )

            class_model["class_variables"] = self.get_variables(
                class_element, "class_variables"
            )
            class_model["object_variables"] = self.get_variables(
                class_element, "object_variables"
            )
            class_data.append(class_model)

        return class_data

    def get_variables(self, class_element: dict, cls_obj: str) -> list:
        """Retrieves either "class_variables" or "object_variables" (depending on cls_obj) from the class_element.

        :param class_element: Parsepy element containing information about a single class
        :type class_element: dict
        :param cls_obj: either "class_variables" or "object_variables"
        :type cls_obj: str
        :returns: list - Collection of all the class/object variables from the given class
        """
        variables = []
        for element in class_element.get(cls_obj, []):
            variables.append(element)
        return variables

    def collect_class_methods(
        self, class_name: str, module_methods: List[dict]
    ) -> List[str]:
        """Retrieves the methods of the class.

        :param class_name: Name of the extracted class
        :type class_name: str
        :param module_methods: Collection of all the functions in the file
        :type module_methods: List[dict]
        :returns: list - Collection of all the class methods of the class with the given name
        """
        return [
            method.get("name")
            for method in module_methods
            if method.get("parent_class") == class_name
        ]
