import os
import pprint

from blackdoc.parser.classes_extractor import ClassesExtractor
from blackdoc.parser.fileParser import FileParser
from blackdoc.parser.methods_extractor import MethodsExtractor
from blackdoc.parser.exceptions_extractor import ExceptionsExtractor
import logging

logger = logging.getLogger(__name__)
SUPPORTED_LANGUAGES = ("java", "js", "py", "R", "rb", "go", "php", "cpp", "cp", "C")
PREFABS_EXPLANATIONS = {}


class DocumentFile:
    def __init__(self, filename: str, file_path: str, nlp_utilities):
        self.nlp_utilities = nlp_utilities
        self.filename = filename
        self.file_path = file_path
        self.parser = None
        self.documented_classes = []
        self.documented_methods = []

    def document_file(self):
        pass

    def parse_file(self, file_path: str):
        self.parser = FileParser(file_path)

    def identify_element_2_document(self, parser):
        pass

    def generate_element_docstring(self, filename: str, file_path: str, nlp_utilities):
        """
        Generally speaking, when two nouns (common nouns, not name of people), the second word has 'posession'
        of the first word (e.g. thread manager -> manager of threads). Anyway, usually it's the last word the control
        (e.g. commit message generator functionality -> functionality of commit message generator (/generation)).
        When there is a nuon and an adjective, the adjective is referring to the nuon and nothing has to change.
        This is also true for the case of a single noun.
        """
        result = {}
        files_documentation = []

        if not os.path.exists(file_path):
            return

        file_documentation = []
        classes_file_info = ClassesExtractor(
            self.parser.get_classes(), self.parser.get_functions()
        )
        classes_file_info.findClasses()
        classes_info = classes_file_info.getClasses()
        exc = ExceptionsExtractor(file_path)
        extracted_exceptions = exc.extract_exceptions()

        try:
            methods_file_info = MethodsExtractor(path_to_repo=file_path)
            methods_info = methods_file_info.collect_repo_methods()
        except Exception as ex:
            methods_info = None
            logger.error("Could not extract methods from %s.\n%s", file_path, ex)

        for element in file["elements"]:
            documentation = ""
            if element["score"] < 0.5:
                if element["element_type"] == "class":
                    documentation = self.generate_class_documentation(
                        element["element_name"],
                        classes_info=classes_info,
                        nlp_utilities=nlp_utilities,
                    )
                elif "method" in element["element_type"]:
                    documentation = self.generate_method_documentation(
                        element["element_name"],
                        methods_info=methods_info,
                        classes_info=classes_info,
                        nlp_utilities=nlp_utilities,
                        exceptions_info=extracted_exceptions,
                    )

            file_documentation.append(
                {
                    "element_name": element["element_name"],
                    "element_type": element["element_type"],
                    "generated": False if element["score"] >= 0.5 else True,
                    "documentation": documentation,
                }
            )

        files_documentation.append(
            {
                "filename": filename,
                "file_path": file_path,
                "elements": file_documentation,
            }
        )
        result["files"] = files_documentation
        return result

    @staticmethod
    def tokenize_identifier(element_name: str, nlp_utilities) -> list:
        separated_words = nlp_utilities.use_segmenter(element_name)
        corrected_words = nlp_utilities.use_spell_checker(separated_words)
        separated_corrected_words = " ".join([word for word in corrected_words])
        return nlp_utilities.use_pos_dependency_tagger([separated_corrected_words])[0]

    def generate_class_documentation(
        self, element_name, classes_info: list, nlp_utilities
    ) -> str:
        """
        documentation generation functionality
        documentation NOUN compound []
        generation NOUN compound [documentation]
        functionality NOUN ROOT [generation]

        round ball
        round PROPN compound []
        ball PROPN ROOT [round]

        thread manager
        thread PROPN compound []
        manager NOUN ROOT [thread]
        """
        docstring = self.describe_class(element_name, nlp_utilities)
        class_info = [
            chosen_class
            for chosen_class in classes_info
            if chosen_class["class_name"] == element_name
        ]

        if class_info:
            class_info = class_info[0]
            parameters = self.class_docstring_parameters(class_info)

        else:
            # pprint.pprint(classes_info)
            parameters = ""

        return docstring + parameters

    def describe_class(self, element_name, nlp_utilities):
        """
            Uses the class name to create a 'description' of the class.
            E.g. RoundBall -> This class represents a round ball.
        """
        # TODO: Improve by considering also "this class represents a ..."
        result = "\nThis class represents"

        tokenized_phrase = self.tokenize_identifier(element_name, nlp_utilities)
        if (
            len([word for word in tokenized_phrase if word["pos_tag"] == "NOUN"]) >= 1
            and len([word for word in tokenized_phrase if word["pos_tag"] == "NOUN"])
            >= 0
        ):
            root_word = [word for word in tokenized_phrase if word["role"] == "ROOT"]

            if len(root_word) == 1:
                result += " the/a " + root_word[0]["word"]
                tokenized_phrase.remove(root_word[0])
                result += (
                    " of " + " ".join([word["word"] for word in tokenized_phrase]) + "s"
                )

            else:
                result += (
                    " " + " ".join([word["word"] for word in tokenized_phrase]) + "s"
                )

        else:
            result += " " + " ".join([word["word"] for word in tokenized_phrase]) + "s"

        return result + "."

    @staticmethod
    def class_docstring_parameters(class_info: dict) -> str:
        # TODO Check why sometimes it truncates the last 2 letters
        if not class_info["inheritance"]:
            info = ""
        else:
            info = (
                " Extend "
                + ("class " if len(class_info["inheritance"]) == 1 else "classes ")
                + ", ".join(class_info["inheritance"])[:-2]
            )

        # TODO Change "Methods:\n" and "Attributs:\n" to be
        # Attributes
        # __________
        # ... (attr : type if type is known)
        # Methods
        # _______
        # ... (the methods with their signature)

        info += "\nMethods:\n"
        for method in class_info["methods"]:
            info += ":method " + method["name"] + ":\n"

        info += "\nAttributes:\n"
        for attr in class_info["variables"]:
            info += ":ivar " + attr + ":\n"

        return info

    def generate_method_documentation(
        self,
        element_name: str,
        nlp_utilities,
        exceptions_info: list,
        methods_info: dict = None,
        classes_info: list = None,
    ) -> str:
        class_info = [
            chosen_class
            for chosen_class in classes_info
            if any(method["name"] == element_name for method in chosen_class["methods"])
        ]

        if len(class_info) > 0:
            class_info = class_info[0]
            class_method_info = [
                method
                for method in class_info["methods"]
                if method["name"] == element_name
            ][0]

        else:
            class_method_info = {}
            class_info = {}

        if methods_info is not None:
            method_info = [
                element
                for element in methods_info["module_methods"]
                if element["name"] == element_name
            ][0]

        else:
            method_info = {}

        method_exceptions = []
        if len(exceptions_info) > 0:
            method_exceptions = [
                exceptions["exceptions_handled"]
                for exceptions in exceptions_info
                if exceptions["starting_line"] > class_method_info["start_line"]
                and exceptions["ending_line"] < class_method_info["end_line"]
            ]
            if len(method_exceptions) > 0:
                method_exceptions = method_exceptions[0]

        result = self.describe_method(
            element_name, nlp_utilities, class_info, class_method_info, method_info
        )

        if methods_info is not None or class_info:
            result = self.method_docstring_parameters(
                result, method_info, class_method_info
            )

        if len(method_exceptions) > 0:
            result = self.method_docstring_exceptions(result, method_exceptions)

        return result

    def describe_method(
        self, element_name, nlp_utilities, class_info, class_method_info, method_info
    ) -> str:
        if element_name in PREFABS_EXPLANATIONS:
            result = ""
        #     TODO
        else:
            result = "\nThis method "
            tokenized_phrase = self.tokenize_identifier(element_name, nlp_utilities)

            if (
                tokenized_phrase[0]["pos_tag"] == "VERB"
                or tokenized_phrase[0]["word"] in nlp_utilities.initialize_verbs()
            ):
                stemmed_word = nlp_utilities.use_words_stemmer(
                    [tokenized_phrase[0]["word"]]
                )
                tokenized_phrase.pop(0)
                result += (
                    "is for "
                    + stemmed_word[0]["stemmed"]
                    + "ing"
                    + (
                        "."
                        if len(tokenized_phrase) == 0
                        else " the "
                        + " ".join([word["word"] for word in tokenized_phrase])
                    )
                )
            else:
                result += (
                    "performs "
                    + (
                        "an "
                        if any(
                            tokenized_phrase[0]["word"][0] in vocal
                            for vocal in ["a", "e", "i", "o", "u"]
                        )
                        else "a "
                    )
                    + " ".join([word["word"] for word in tokenized_phrase])
                    + "."
                )

        if len(method_info) != 0:
            # In case parsepy worked

            if method_info["type"] == "class_method":
                result += " This function is a "

                if (
                    len(method_info["parameters"]) == 0
                    or method_info["parameters"][0]["name"] != "self"
                ):
                    result += "static "

                return (
                    result
                    + "class method of "
                    + method_info["context"]["context_name"]
                    + "."
                )

        else:
            # In case there was a problem with parsepy

            if len(class_info) > 0:
                result += " This function is a "

                if (
                    len(class_method_info["parameters"]) == 0
                    or class_method_info["parameters"][0]["parameter_name"] != "self"
                ):
                    result += "static "

                return result + "class method of " + class_info["class_name"] + "."

        return result + "This function is a global method."

    @staticmethod
    def method_docstring_parameters(result, method_info, class_method_info) -> str:
        arguments = []

        if method_info is not None:
            if "self" == method_info["parameters"][0]["name"]:
                method_info["parameters"].pop(0)

            for argument in method_info["parameters"]:
                try:
                    arguments.append(
                        {
                            "name": argument["name"],
                            "type": ""
                            if not argument["param_type_hint"]
                            else argument["param_type_hint"],
                            "default": argument["value"],
                        }
                    )
                except Exception as exc:
                    print(exc)
                    pprint.pprint(argument)
                    pprint.pprint(class_method_info)
                    input()
        else:
            if (
                len(class_method_info["parameters"]) > 0
                and class_method_info["parameters"][0] == "self"
            ):
                class_method_info["parameters"].pop(0)

            for argument in class_method_info["parameters"]:
                arguments.append(
                    {
                        "name": argument["parameter_name"],
                        "type": ""
                        if argument["parameter_type"] == "N/A"
                        else argument["parameter_type"],
                        "default": argument["parameter_default_value"],
                    }
                )

        for param in arguments:
            # TODO: change "defaults to ..." to "(Default value = ...)"
            result += "\n:param " + param["name"] + ": "

        for param in arguments:
            if len(param["type"]) > 0:
                result += (
                    "\n:type "
                    + param["name"]
                    + ": "
                    + param["type"]
                    + (
                        ". It defaults to " + param["default"]
                        if param["default"] and param["default"] != "N/A"
                        else ""
                    )
                )

        return result

    @staticmethod
    def method_docstring_exceptions(result, exceptions) -> str:
        if exceptions:
            result += "\n:raises: " + ", ".join(
                [
                    exception["exception_name"]
                    + (
                        " as " + exception["exception_alias"]
                        if exception["exception_alias"] != "N/A"
                        else ""
                    )
                    for exception in exceptions
                ]
            )
        return result
