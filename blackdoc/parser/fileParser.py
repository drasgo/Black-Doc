import os

from pythonparser.parser import Parser


class FileParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.code = self.get_code()

        if self.code:
            self.parser = Parser(code=self.code)
            self.parser.parse()

    def get_code(self) -> str:
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as fp:
                return fp.read()
        else:
            return ""

    def get_classes(self):
        return self.parser.classes()

    def get_functions(self):
        return self.parser.functions()

    def get_exceptions(self):
        return self.parser.exceptions()
