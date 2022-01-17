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
        self.sorted_elements = []
        self.classes = []
        self.functions = []
        self.exceptions = []

        self.code = self._get_code()

    def _get_code(self) -> str:
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as fp:
                return fp.read()
        else:
            return ""

    def _set_code(self):
        with open(self.file_path, "w") as fp:
            fp.write(self.code)

    def parse_code(self) -> bool:
        self.parser = FileParser(self.code)
        return self.parser.check_code_validity()

    def document_file(self):
        if not self.parse_code() or \
            (not self.parser.get_classes() and not self.parser.get_functions()):
            return

        self.classes = ClassesExtractor(self.parser.get_classes(), self.parser.get_functions()).collect_data()
        self.functions = MethodsExtractor(self.parser.get_functions()).collect_data()
        self.exceptions = ExceptionsExtractor(self.parser.get_exceptions()).collect_data()

        self.sorted_elements = sorted(
                        self.classes + self.functions,
                        key=lambda elem: elem.get("start_line"), reverse=True
                        )

        for elem_index in range(len(self.sorted_elements)):
            current_elem = self.sorted_elements[elem_index]
            try:
                if (elem_index == 0 or
                not any(current_elem.get("start_line") == prev_elem.get("start_line")
                        for prev_elem in self.sorted_elements[:elem_index])) and \
                not current_elem.get("documentation").strip():
                # current_elem.get("name").strip() == "TensorNode":
                    new_docstring = self.generate_element_docstring(current_elem)
                    self.add_docstring_2_code_element(new_docstring, current_elem.get("start_line"))
            except Exception as exc:
                print(exc)
                pprint.pprint(current_elem)
                input()
        if self.parse_code():
            self._set_code()
        return

    def add_docstring_2_code_element(self, docstring: str, start_line: int) -> str:
        new_code = self.code.split("\n")
        existing_docstring = False
        start_line = start_line - 1
        first_line = -1

        for line_index in range(start_line, len(new_code)):
            if first_line == -1 and new_code[line_index].strip().endswith(":"):
                first_line = line_index
                continue

            if first_line != -1 and not existing_docstring and \
                any(new_code[line_index].strip().startswith(mark) and
                    new_code[line_index].strip().count(mark) % 2 != 0
                    for mark in ("'''", '"""')):
                existing_docstring = True
                continue

            if first_line != -1 and existing_docstring and \
                    any(new_code[line_index].strip().endswith(mark) and
                        new_code[line_index].strip().count(mark) % 2 != 0
                        for mark in ("'''", '"""')):
                existing_docstring = False
                continue

            if first_line != -1 and not existing_docstring and new_code[line_index].strip():
                new_code = new_code[:first_line + 1] + \
                           docstring.split("\n") + \
                           [""] + \
                           new_code[line_index:]
                break
        print("final result in code")
        print("\n".join(new_code[start_line: start_line + 35]))
        input()
        return "\n".join(new_code)

    def generate_element_docstring(self, element: dict) -> str:
        """
        Generally speaking, when two nouns (common nouns, not name of people), the second word has 'posession'
        of the first word (e.g. thread manager -> manager of threads). Anyway, usually it's the last word the control
        (e.g. commit message generator functionality -> functionality of commit message generator (/generation)).
        When there is a nuon and an adjective, the adjective is referring to the nuon and nothing has to change.
        This is also true for the case of a single noun.
        """
        tabs = self.get_tabs(element)
        quote_marks = '"""'

        if element.get("genus") == "class":
            documentation = self.generate_class_documentation(element, tabs)
        else:
            documentation = self.generate_method_documentation(
                            element,
                            exceptions_info=self.exceptions,
                            tabs=tabs
                        )

        return f"{tabs}{quote_marks}\n{documentation.rstrip()}\n{tabs}{quote_marks}"

    # Class documentation

    def generate_class_documentation(self, class_element: dict, tabs: str) -> str:
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
        # TODO
        print("doing class " + class_element.get("name"))

        docstring = ""
        # docstring = self.describe_class(class_element.get("name"), tabs)
        parameters = self.class_docstring_parameters(class_element, tabs)
        return docstring + parameters

    def class_docstring_parameters(self, class_element: dict, tabs: str) -> str:
        if not class_element["inheritance"]:
            info = ""
        else:
            info = f"{tabs}Extends " \
                   f"{('class ' if len(class_element['inheritance']) == 1 else 'classes ')}" \
                   f"{', '.join(class_element['inheritance'])}.\n\n"
        print("post inheritance")
        print(info)

        if class_element.get("methods"):
            info += f"{tabs}Methods:\n"
            for method in set(class_element["methods"]):
                info += f"{tabs}:method {method}:\n"
            info += "\n"

        if class_element.get("class_variables"):
            info += f"\n{tabs}Attributes:\n"
            for attr in class_element["class_variables"]:
                info += f"{tabs}:ivar {attr.get('name')}: \n"
            info += "\n"

        if class_element["__init__"]:
            if class_element["__init__"]["documentation"]:
                for line in class_element["__init__"]["documentation"].strip().split("\n"):
                    info += f"{tabs}{line.strip()}\n"
            else:
                info += self.method_docstring_parameters(class_element["__init__"], tabs)
            info += "\n"
        return info

    # Functions and Methods

    def generate_method_documentation(
        self,
        method_element: dict,
        exceptions_info: list,
        tabs: str = ""
    ) -> str:
        print("doing method " + method_element.get("name"))
        method_exceptions = []
        if exceptions_info:
            method_exceptions = [
                exceptions["exceptions_handled"]
                for exceptions in exceptions_info
                if exceptions["starting_line"] > method_element["start_line"]
                and exceptions["ending_line"] < method_element["end_line"]
            ]

        # TODO
        result = ""
        # result = self.describe_method(element)
        result += self.method_docstring_parameters(method_element, tabs)

        if method_exceptions:
            result += self.method_docstring_exceptions(method_exceptions, tabs)

        return result

    @staticmethod
    def method_docstring_parameters(method_info: dict, tabs: str) -> str:
        result = ""
        arguments = []

        for argument_index in range(len(method_info["parameters"])):
            argument = method_info["parameters"][argument_index]

            if "self" == argument["name"] and argument_index == 0:
                continue

            arguments.append(
                {
                    "name": argument["name"],
                    "type": ""
                    if not argument["param_type_hint"]
                    else argument["param_type_hint"],
                    "default": argument["value"],
                }
            )

        for param in arguments:
            result += f"\n{tabs}:param {param['name']}: XXX"

            if param["default"]:
                if param["type"] == "str":
                    result += f'. (Default="{param["default"]}")'
                else:
                    result += f'. (Default={param["default"]})'

            if param["type"]:
                result += f"\n{tabs}:type {param['name']}: {param['type']}"
        return result

    @staticmethod
    def method_docstring_exceptions(exceptions, tabs: str) -> str:
        result = ""
        for exception in exceptions:
            result += f"\n{tabs}:raises {', '.join([exception['exception_name']])}: XXX"
        return result

    # NLP-based

    @staticmethod
    def get_tabs(element: dict) -> str:
        return "\t" * (len(element.get("complete_context")))

    def tokenize_identifier(self, element_name: str) -> list:
        separated_words = self.nlp_utilities.use_segmenter(element_name)
        corrected_words = self.nlp_utilities.use_spell_checker(separated_words)
        separated_corrected_words = " ".join([word for word in corrected_words])
        return self.nlp_utilities.use_pos_dependency_tagger(
            [separated_corrected_words]
        )[0]

    def describe_class(self, element_name):
        """
            Uses the class name to create a 'description' of the class.
            E.g. RoundBall -> This class represents a round ball.
        """
        # TODO: Improve by considering also "this class represents a ..."
        result = "\nThis class represents"

        tokenized_phrase = self.tokenize_identifier(element_name)
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

    def describe_method(self, element: dict) -> str:
        # TODO
        element_name = element.get("name")
        if element_name in PREFABS_EXPLANATIONS:
            result = ""
        #     TODO
        else:
            result = "\nThis method "
            tokenized_phrase = self.tokenize_identifier(element_name)

            if (
                tokenized_phrase[0]["pos_tag"] == "VERB"
                or tokenized_phrase[0]["word"] in self.nlp_utilities.initialize_verbs()
            ):
                stemmed_word = self.nlp_utilities.use_words_stemmer(
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

        if element["type"] == "class_method":
            result += " This function is a "

            if (
                len(element["parameters"]) == 0
                or element["parameters"][0]["name"] != "self"
            ):
                result += "static "

            return f"{result} class method of {element['context']['context_name']}."
        else:
            return result + "This function is a global method."
