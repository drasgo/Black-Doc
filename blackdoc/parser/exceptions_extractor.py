from typing import List


class ExceptionsExtractor:
    def __init__(self, parsed_exceptions):
        self.exceptions = parsed_exceptions

    def collect_data(self) -> List[dict]:
        """
        Tries to parse (via `py:parsepy.Parser`) the exceptions in the module at module_path.
        If parsing does not succeed returns an empty list
        """
        return self.exceptions
