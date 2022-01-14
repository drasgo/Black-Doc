import argparse
import multiprocessing

import os
import shutil
import json

from nlputilities.nlp import NLPUtilities

from blackdoc.black_repo import black_file, black_repo
from blackdoc.docstring import DocumentFile

__version__ = "0.8.0"

DEFAULT_WORKERS = 2


def get_cli_argument_parser() -> argparse.ArgumentParser:
    """
    Allows the user to pass arguments through CLI when executing the program.

    :returns: argparse.ArgumentParser - the object for retrieving the parsed arguments passed to the CLI
    """
    cli_arg_parser = argparse.ArgumentParser(
        usage="%(prog)s .",
        description="Executes the black library and generates a template docstring for every non-documented function"
        "and class of the current repository.",
    )

    cli_arg_parser.add_argument(
        "-b",
        "--backup",
        help="Creates a backup folder called 'blackdoc_backup' (if the folder backup does not exist, otherwise it exits) "
        "(Default True).",
        action="store_true",
        default=True,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-n",
        "--no_black",
        help="Does not perform the black operations, and only generates the docstring templates (Default False).",
        action="store_true",
        required=False,
    )

    cli_arg_parser.add_argument(
        "-f",
        "--file",
        help="If a single file is specified, then the 'black & doc' process is executed only on the specified file.",
        required=False,
    )

    cli_arg_parser.add_argument(
        "-w",
        "--workers",
        help="Number of workers that document the files in the repository in parallel (Default=1).",
        required=False,
    )

    return cli_arg_parser


def document_file(file_name: str, file_path: str):
    docs = DocumentFile(file_name, file_path, nlp_utilities)
    docs.document_file()
    return


if __name__ == "__main__":
    curr_dir = __file__[: __file__.rfind("/")]

    arg_parser = get_cli_argument_parser()
    cli_arguments = arg_parser.parse_args()

    workers = DEFAULT_WORKERS if not cli_arguments.workers else cli_arguments.workers

    if cli_arguments.backup:
        shutil.copytree(curr_dir, curr_dir + "/blackdoc_backup")

    # Initialize nlp utilities once for every worker
    nlp_utilities = NLPUtilities
    nlp_utilities.initialize_segmenter()
    nlp_utilities.initialize_spell_checker()
    nlp_utilities.initialize_spacy()
    nlp_utilities.initialize_verbs()
    nlp_utilities.initialize_stemmer()

    if cli_arguments.file:
        curr_file = curr_dir + "/" + cli_arguments.file
        filename = (
            cli_arguments.file
            if "/" not in cli_arguments.file
            else cli_arguments.file.split("/")[-1]
        )

        if not cli_arguments.no_black:
            black_file(curr_file)

        document_file(filename, curr_file)

    else:
        ignored_folders = json.load(open("ignored_directories.json", "r"))
        black_repo()

        files = []
        for dirpath, dirnames, filenames in os.walk(curr_dir, topdown=True):
            relative_path = dirpath.replace(curr_dir, "")
            if any(
                subfolder == ignored
                for subfolder in relative_path.split("/")
                for ignored in ignored_folders.get("ignored_directories", [])
            ):
                continue

            for single_file in filenames:
                if single_file.endswith(".py"):
                    files.append((single_file, os.path.join(dirpath, single_file)))

        if workers > 1:
            with multiprocessing.Pool(processes=workers) as pool:
                _ = pool.starmap(document_file, files)

        else:
            for arg in files:
                document_file(*arg)
