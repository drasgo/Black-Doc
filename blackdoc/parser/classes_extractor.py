from typing import List


CLASSES_RECORD_KEYS = [
    "name",
    "genus",
    "documentation",
    "start_line",
    "end_line",
    "inheritance",
    "complete_context",
]


class ClassesExtractor:
    """
    This class XXX .

    Methods:
    :method collect_class_methods:
    :method collect_data:
    :method collect_method_body:
    :method __init__:
    :method get_variables:


    :param parsed_classes: XXX
    :param parsed_functions: XXX
    """

    def __init__(self, parsed_classes, parsed_functions):
        """
        This overrides the built-in object Initializator. It is a class method of ClassesExtractor.

        :param parsed_classes: XXX
        :param parsed_functions: XXX
        """

        self.classes = parsed_classes
        self.functions = parsed_functions

    def collect_data(self) -> List[dict]:
        """
        Tries to parse (via `py:parsepy.Parser`) the classes in the module at module_path, and save the extracted results
        in collected_data.
        If parsing does not succeed an empty list is saved instead
        """
        class_data = list()

        for class_element in self.classes:
            class_model = dict()

            class_model["total_lines"] = (
                class_element["end_line"] - class_element["start_line"] + 1
            )

            class_model["methods"] = self.collect_class_methods(
                class_element.get("name", ""), self.functions
            )

            class_model["__init__"] = self.collect_method_body(
                class_element.get("name", ""), "__init__", self.functions
            )

            class_model["class_variables"] = self.get_variables(
                class_element, "class_variables"
            )
            class_model["object_variables"] = self.get_variables(
                class_element, "object_variables"
            )
            class_model.update(
                {k: class_element.get(k, None) for k in CLASSES_RECORD_KEYS}
            )
            class_data.append(class_model)

        return class_data

    @staticmethod
    def get_variables(class_element: dict, cls_obj: str) -> list:
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

    @staticmethod
    def collect_method_body(
        class_name: str, method_name: str, module_methods: List[dict]
    ) -> dict:
        """
        This method is XXX . It is a static class method of ClassesExtractor.

        :param class_name: XXX
        :type class_name: str
        :param method_name: XXX
        :type method_name: str
        :param module_methods: XXX
        :type module_methods: List[dict]
        :returns: dict - XXX
        """

        body = [
            method
            for method in module_methods
            if method.get("parent_class") == class_name
            and method.get("name") == method_name
        ]
        return body[0] if body else {}

    @staticmethod
    def collect_class_methods(class_name: str, module_methods: List[dict]) -> List[str]:
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
