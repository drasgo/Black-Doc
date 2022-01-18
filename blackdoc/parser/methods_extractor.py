import logging
from typing import List

logger = logging.getLogger(__name__)

METHODS_RECORD_KEYS = [
    "name",
    "genus",
    "parent_class",
    "start_line",
    "end_line",
    "total_lines",
    "num_lines_of_code",
    "star_parameters_count",
    "number_parameters",
    "number_annotated_parameters",
    "parameters",
    "context",
    "returns",
    "documentation",
    "complete_context",
]


class MethodsExtractor:
    """
    Utility class based on pyparser.
    Parser for collecting methods in Python-modules of a repository.
    """

    def __init__(self, parsed_functions):
        self.functions = parsed_functions

    def collect_data(self) -> List[dict]:
        """
        Tries to parse (via `py:parsepy.Parser`) the methods (class and global) in the module at module_path.
        If parsing does not succeed returns an empty list
        """
        # Iterate over functions computing some extra data not contained in the parsepy returned data
        for f in self.functions:
            if "documentation" in f:
                f["num_lines_of_code"] = (
                    f["total_lines"] - len(f["documentation"].splitlines())
                    if f["documentation"]
                    else f["total_lines"]
                )
            if "parameters" in f:
                f["number_parameters"] = (
                    len(f["parameters"]) if f["parameters"] is not None else 0
                )
                try:
                    f["number_annotated_parameters"] = (
                        len(
                            [
                                p
                                for p in f["parameters"]
                                if len(p["param_type_hint"]) > 0
                            ]
                        )
                        if f["number_parameters"]
                        else 0
                    )
                except Exception as ex:
                    logger.error(
                        "The following exception was raised while analyzing  annotated parameters: %s",
                        type(ex).__name__,
                    )
                    f["number_annotated_parameters"] = 0
        module_methods = [
            {k: f.get(k, None) for k in METHODS_RECORD_KEYS}
            for f in self.functions
        ]
        return module_methods
