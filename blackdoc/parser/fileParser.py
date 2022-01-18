from typing import List

from pythonparser.parser import Parser


class FileParser:
    """
    This class XXX .

    Methods:
    :method check_code_validity:
    :method get_exceptions:
    :method __init__:
    :method get_functions:
    :method get_classes:


    :param code: XXX
    :type code: str
    """

    def __init__(self, code: str):
        """
        This overrides the built-in object Initializator. It is a class method of FileParser.

        :param code: XXX
        :type code: str
        """

        self.code = code
        self.parser = Parser(code=self.code)
        self.parser.parse()

    def check_code_validity(self) -> bool:
        """
        This method is XXX . It is a class method of FileParser.

        :returns: bool - XXX
        """

        return True if self.code and \
                       not self.parser.parsing_status() else False

    def get_classes(self) -> List[dict]:
        """
        This is a getter method. This method is XXX . It is a class method of FileParser.

        :returns: List[dict] - XXX
        """

        return self.parser.classes()

    def get_functions(self) -> List[dict]:
        """
        This is a getter method. This method is XXX . It is a class method of FileParser.

        :returns: List[dict] - XXX
        """

        return self.parser.functions()

    def get_exceptions(self) -> List[dict]:
        """
        This is a getter method. This method is XXX . It is a class method of FileParser.

        :returns: List[dict] - XXX
        """

        return self.parser.exceptions()
