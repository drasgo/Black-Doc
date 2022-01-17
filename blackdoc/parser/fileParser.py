from typing import List

from pythonparser.parser import Parser


class FileParser:
    def __init__(self, code: str):
        self.code = code
        self.parser = Parser(code=self.code)
        self.parser.parse()

    def check_code_validity(self) -> bool:
        return True if self.code and \
                       not self.parser.parsing_status() else False

    def get_classes(self) -> List[dict]:
        return self.parser.classes()

    def get_functions(self) -> List[dict]:
        return self.parser.functions()

    def get_exceptions(self) -> List[dict]:
        return self.parser.exceptions()
