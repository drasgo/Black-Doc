from typing import List


class ExceptionsExtractor:
    """
    This class XXX .

    Methods:
    :method collect_data:
    :method __init__:


    :param parsed_exceptions: XXX
    """

    def __init__(self, parsed_exceptions):
        """
        This overrides the built-in object Initializator. It is a class method of ExceptionsExtractor.

        :param parsed_exceptions: XXX
        """

        self.exceptions = parsed_exceptions

    def collect_data(self) -> List[dict]:
        """
        Tries to parse (via `py:parsepy.Parser`) the exceptions in the module at module_path.
        If parsing does not succeed returns an empty list
        """
        return self.exceptions
