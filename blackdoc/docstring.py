import os

from blackdoc.parser.classes_extractor import ClassesExtractor
from blackdoc.parser.fileParser import FileParser
from blackdoc.parser.methods_extractor import MethodsExtractor
from blackdoc.parser.exceptions_extractor import ExceptionsExtractor
import logging

logger = logging.getLogger(__name__)
PREFAB_METHOD_EXPLANATIONS = {
    "get": "This is a getter method.",
    "add": "This is an adder method.",
    "set": "This is a setter method."
}

PREFAB_METHOD_DESCRIPTIONS = {
    "__init__": "This overrides the built-in object Initializator.",
    "__del__": "This overrides the built-in object Destructor.",
    "__new__": "This overrides the built-in object Constructor.",
    "__repr__": "This overrides the built-in (Formal) String representation of the object.",
    "__str__": "This overrides the built-in (Informal) String representation of the object.",
    "__format__": "This overrides the built-in Formatted string representation of the object.",
    "__bytes__": "This overrides the built-in Bytes representation of the object.",
    "__bool__": "This overrides the built-in Boolean representation of the object.",
    "__hash__": "This overrides the built-in Hash representation of the object.",
    "__call__": "This overrides the built-in behaviour when the object is called like a function.",
    "__lt__": "This describes how the object behaves when the Less Than operation is performed with it.",
    "__le__": "This describes how the object behaves when the Less or Equal operation is performed with it.",
    "__eq__": "This describes how the object behaves when the Equal operation is performed with it.",
    "__ne__": "This describes how the object behaves when the Not Equal operation is performed with it.",
    "__gt__": "This describes how the object behaves when the Greater Than operation is performed with it.",
    "__ge__": "This describes how the object behaves when the Greater or Equal operation is performed with it.",
    "__mul__": "This describes how the object behaves when the multiplication operation is performed with it.",
    "__add__": "This describes how the object behaves when the sum operation is performed with it.",
    "__div__": "This describes how the object behaves when the division operation is performed with it.",
    "__sub__": "This describes how the object behaves when the subtraction operation is performed with it.",
    "__iter__": "This defines how to iterate through the object, when an iteration operation is performed on it.",
    "__next__": "This defines how to retrieve the next element when iterating through the object.",
    "__len__": "This overrides the built-in Lenght representation of the object.",
    "__contains__": "This overrides the representation of the elements contained in the object.",
    "__copy__": "This overrides the Copy operation of the current object.",
}


class DocumentFile:
    """
    This class XXX .

    Methods:
    :method add_docstring_2_code_element:
    :method get_tabs:
    :method _get_code:
    :method generate_class_documentation:
    :method describe_method:
    :method method_docstring_exceptions:
    :method parse_code:
    :method generate_element_docstring:
    :method __init__:
    :method document_file:
    :method class_docstring_parameters:
    :method method_docstring_parameters:
    :method generate_method_documentation:
    :method tokenize_identifier:
    :method _set_code:
    :method cleanup_code:
    :method describe_class:


    :param filename: XXX
    :type filename: str
    :param file_path: XXX
    :type file_path: str
    :param nlp_utilities: XXX
    """

    def __init__(self, filename: str, file_path: str, nlp_utilities):
        """
        This overrides the built-in object Initializator. It is a class method of DocumentFile.

        :param filename: XXX
        :type filename: str
        :param file_path: XXX
        :type file_path: str
        :param nlp_utilities: XXX
        """

        self.nlp_utilities = nlp_utilities
        self.filename = filename
        self.file_path = file_path
        self.parser = None
        self.sorted_elements = []
        self.classes = []
        self.functions = []
        self.exceptions = []
        self.no_nlp = True if not nlp_utilities else False
        self.code = self._get_code()

    def _get_code(self) -> str:
        """
        This method is XXX . It is a class method of DocumentFile.

        :returns: str - XXX
        """

        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as fp:
                return fp.read()
        else:
            return ""

    @staticmethod
    def cleanup_code(code):
        """
        This method is XXX . It is a static class method of DocumentFile.

        :param code: XXX
        """

        return code.replace("\t", "    ")

    def _set_code(self):
        """
        This method is XXX . It is a class method of DocumentFile.
        """

        with open(self.file_path, "w") as fp:
            fp.write(self.code)

    def parse_code(self) -> bool:
        """
        This method is XXX . It is a class method of DocumentFile.

        :returns: bool - XXX
        """

        self.parser = FileParser(self.code)
        return self.parser.check_code_validity()

    def document_file(self):
        """
        This method is XXX . It is a class method of DocumentFile.
        """

        if not self.parse_code() or \
                (not self.parser.get_classes() and not self.parser.get_functions()):
            return False

        self.classes = ClassesExtractor(self.parser.get_classes(), self.parser.get_functions()).collect_data()
        self.functions = MethodsExtractor(self.parser.get_functions()).collect_data()
        self.exceptions = ExceptionsExtractor(self.parser.get_exceptions()).collect_data()

        self.sorted_elements = sorted(
            self.classes + self.functions,
            key=lambda elem: elem.get("start_line"), reverse=True
        )

        for elem_index in range(len(self.sorted_elements)):
            current_elem = self.sorted_elements[elem_index]
            if (elem_index == 0 or
                not any(current_elem.get("start_line") == prev_elem.get("start_line")
                        for prev_elem in self.sorted_elements[:elem_index])) and \
                    not current_elem.get("documentation").strip():
                new_docstring = self.generate_element_docstring(current_elem)
                self.code = self.add_docstring_2_code_element(new_docstring, current_elem.get("start_line"))

        self.code = self.cleanup_code(self.code)
        if not self.parse_code():
            return False

        self._set_code()
        return True

    def add_docstring_2_code_element(self, docstring: str, start_line: int) -> str:
        """
        This is an adder method. This method is XXX . It is a class method of DocumentFile.

        :param docstring: XXX
        :type docstring: str
        :param start_line: XXX
        :type start_line: int
        :returns: str - XXX
        """

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

        return f"{tabs}{quote_marks}\n{tabs}{documentation.strip()}\n{tabs}{quote_marks}"

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
        docstring = self.describe_class(class_element.get("name"), tabs)
        parameters = self.class_docstring_parameters(class_element, tabs)
        return docstring + parameters

    def class_docstring_parameters(self, class_element: dict, tabs: str) -> str:
        """
        This method is XXX . It is a class method of DocumentFile.

        :param class_element: XXX
        :type class_element: dict
        :param tabs: XXX
        :type tabs: str
        :returns: str - XXX
        """
        if not class_element["inheritance"]:
            info = ""

        else:
            info = f"\n{tabs}It extends the " \
                   f"{('class ' if len(class_element['inheritance']) == 1 else 'classes ')}" \
                   f"{', '.join(class_element['inheritance'])}.\n\n"

        if class_element.get("methods"):
            info += f"\n{tabs}Methods:\n"
            for method in set(class_element["methods"]):
                info += f"{tabs}:method {method}: XXX\n"
            info += "\n"

        # Uncomment to add class attributes to the generated docstring for classes
        # if class_element.get("class_variables"):
        #     info += f"\n{tabs}Attributes:\n"
        #     for attr in class_element["class_variables"]:
        #         info += f"{tabs}:ivar {attr.get('name')}: XXX\n"
        #     info += "\n"

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
        """
        This method is XXX . It is a class method of DocumentFile.

        :param method_element: XXX
        :type method_element: dict
        :param exceptions_info: XXX
        :type exceptions_info: list
        :param tabs: XXX. (Default="")
        :type tabs: str
        :returns: str - XXX
        """
        method_exceptions = []
        if exceptions_info:
            method_exceptions = [
                exceptions["exception"]
                for exceptions in exceptions_info
                if exceptions["start_line"] > method_element["start_line"]
                and exceptions["end_line"] < method_element["end_line"]
            ]

        result = self.describe_method(method_element, tabs)
        result += self.method_docstring_parameters(method_element, tabs)

        if method_exceptions:
            result += self.method_docstring_exceptions(method_exceptions, tabs)

        return result

    @staticmethod
    def method_docstring_parameters(method_info: dict, tabs: str) -> str:
        """
        This method is XXX . It is a static class method of DocumentFile.

        :param method_info: XXX
        :type method_info: dict
        :param tabs: XXX
        :type tabs: str
        :returns: str - XXX
        """
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
                result += f'. (Default={param["default"]})'

            if param["type"]:
                result += f"\n{tabs}:type {param['name']}: {param['type']}"

        if method_info["returns"]:
            result += f"\n{tabs}:returns: {method_info['returns']} - XXX"
        return result

    @staticmethod
    def method_docstring_exceptions(exceptions, tabs: str) -> str:
        """
        This method is XXX . It is a static class method of DocumentFile.

        :param exceptions: XXX
        :param tabs: XXX
        :type tabs: str
        :returns: str - XXX
        """
        result = ""
        for exception in exceptions:
            result += f"\n{tabs}:raises {', '.join([exception['name']])}: XXX"
        return result

    # NLP-based

    @staticmethod
    def get_tabs(element: dict) -> str:
        """
        This is a getter method. This method is XXX . It is a static class method of DocumentFile.

        :param element: XXX
        :type element: dict
        :returns: str - XXX
        """

        return "\t" * (len(element.get("complete_context")))

    def tokenize_identifier(self, element_name: str) -> list:
        """
        This method is XXX . It is a class method of DocumentFile.

        :param element_name: XXX
        :type element_name: str
        :returns: list - XXX
        """

        separated_words = self.nlp_utilities.use_segmenter(element_name)
        corrected_words = self.nlp_utilities.use_spell_checker(separated_words)
        separated_corrected_words = " ".join([word for word in corrected_words])
        return self.nlp_utilities.use_pos_dependency_tagger(
            [separated_corrected_words]
        )[0]

    def describe_class(self, element_name: str, tabs: str) -> str:
        """
            Uses the class name to create a 'description' of the class.
            E.g. RoundBall -> This class represents a round ball.
        """
        if self.no_nlp:
            return f"{tabs}This class XXX .\n"

        result = f"{tabs}This class represents"

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

        return result + ".\n"

    def describe_method(self, element: dict, tabs: str) -> str:
        """
        This method is XXX . It is a class method of DocumentFile.

        :param element: XXX
        :type element: dict
        :param tabs: XXX
        :type tabs: str
        :returns: str - XXX
        """

        element_name = element.get("name")
        result = f"{tabs}"

        if any(element_name.lower().startswith(prefab) for prefab in PREFAB_METHOD_EXPLANATIONS):
            temp_name = element_name.lower()
            for prefab in PREFAB_METHOD_EXPLANATIONS:
                if temp_name.startswith(prefab):
                    result = f"\n{tabs} {PREFAB_METHOD_EXPLANATIONS[prefab]} "
                    break

        if any(element_name.lower() == prefab for prefab in PREFAB_METHOD_DESCRIPTIONS):
            temp_name = element_name.lower()
            for prefab in PREFAB_METHOD_DESCRIPTIONS:
                if temp_name == prefab:
                    result += f"{PREFAB_METHOD_DESCRIPTIONS[prefab]}"
                    break

        elif self.no_nlp:
            result += "This method is XXX ."

        else:
            result += "This method "
            tokenized_phrase = self.tokenize_identifier(element_name)

            if (
                tokenized_phrase[0]["pos_tag"] == "VERB"
                or tokenized_phrase[0]["word"] in self.nlp_utilities.initialize_verbs()
            ):
                stemmed_word = self.nlp_utilities.use_words_stemmer(
                    [tokenized_phrase[0]["word"]]
                )
                tokenized_phrase.pop(0)
                result += f"is for {stemmed_word[0]['stemmed']}ing" \
                          f"{('.'if not tokenized_phrase else ' the ' + ' '.join([word['word'] for word in tokenized_phrase]))}"
            else:
                result += f"performs " \
                          f"{('an ' if any(tokenized_phrase[0]['word'][0] in vocal for vocal in ['a', 'e', 'i', 'o', 'u']) else 'a ')}" \
                          f"{' '.join([word['word'] for word in tokenized_phrase])}."

        if element["genus"] == "class_method":
            result += f" It is a"

            if (
                not element["parameters"]
                or element["parameters"][0]["name"] != "self"
            ):
                result += " static"

            return f"{result} class method of {element['context']['context_name']}.\n"
        else:
            return f"{result} It is a global method.\n"
