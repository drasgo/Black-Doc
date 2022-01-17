# Silences useless warnings
import os
import warnings
from multiprocessing.managers import BaseManager

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import argparse
import multiprocessing

import shutil

from nlputilities.nlp import NLPUtilities

from blackdoc.black import black_file, black_repo
from blackdoc.configs import log
from blackdoc.docstring import DocumentFile

__version__ = "0.8.0"
DEFAULT_WORKERS = 1
IGNORED_DIRECTORIES = [
    "blackdoc_backup",
    "venv",
    "virtualenv",
    "__pycache__",
    "build",
    "dist",
    "doc",
    "docs",
    "Docs",
    ".git",
    ".gitignore",
    ".idea",
    ".pytest_cache",
    "*.egg-info",
    "html",
]


class NLPManager(BaseManager):
    pass


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
        default=False,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-n",
        "--no_black",
        help="Does not perform the black operations, and only generates the docstring templates (Default False).",
        action="store_true",
        default=True,
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
    log(f"Documenting {file_name}")
    docs = DocumentFile(file_name, file_path, nlp_utilities)
    docs.document_file()
    return


def create_backup(is_backup: bool):
    log("Backing up repository")
    if is_backup:
        if os.path.exists(curr_dir + "/blackdoc_backup"):
            shutil.rmtree(curr_dir + "/blackdoc_backup")
        shutil.copytree(curr_dir, curr_dir + "/blackdoc_backup")


def initialize_NLP():
    log("Loading NLP-based tools")
    NLPManager.register(
        "NLPUtilities",
        NLPUtilities,
        exposed=[
            "initialize_all_datasets",
            "initialize_segmenter",
            "initialize_spell_checker",
            "initialize_spacy",
            "initialize_verbs",
            "initialize_stemmer",
            "use_segmenter",
            "use_spell_checker",
            "use_lemmetizer",
            "check_abbreviation",
            "extend_contraction",
            "use_phrase_checker",
            "use_pos_dependency_tagger",
            "use_words_stemmer",
            "identifier_checker",
            "input_vectorization",
            "english_score",
            "separator_score",
            "get_pos_tags",
        ],
    )
    mymanager = NLPManager()
    mymanager.start()
    toolset = mymanager.NLPUtilities()
    toolset.initialize_segmenter()
    toolset.initialize_spell_checker()
    toolset.initialize_spacy()
    toolset.initialize_verbs()
    toolset.initialize_stemmer()
    log("NLP utilities loaded")
    return toolset


if __name__ == "__main__":
    curr_dir = os.getcwd()
    arg_parser = get_cli_argument_parser()
    cli_arguments = arg_parser.parse_args()

    workers = DEFAULT_WORKERS if not cli_arguments.workers else cli_arguments.workers

    create_backup(cli_arguments.backup)

    # Initialize nlp utilities once for every worker
    nlp_utilities = None
    # nlp_utilities = initialize_NLP()

    if cli_arguments.file:
        curr_file = (
            f"{curr_dir}/{cli_arguments.file}"
            if "/" not in cli_arguments.file
            else cli_arguments.file
        )
        filename = (
            cli_arguments.file
            if "/" not in cli_arguments.file
            else cli_arguments.file.split("/")[-1]
        )

        if not cli_arguments.no_black:
            black_file(curr_file)

        document_file(filename, curr_file)

    else:
        if not cli_arguments.no_black:
            print("Blacking")
            black_repo()

        files = []
        for dirpath, dirnames, filenames in os.walk(curr_dir, topdown=True):
            relative_path = dirpath.replace(curr_dir, "")
            if any(
                subfolder == ignored
                for subfolder in relative_path.split("/")
                for ignored in IGNORED_DIRECTORIES
            ):
                continue

            for single_file in filenames:
                if single_file.endswith(".py") and single_file.endswith("core.py"):
                    files.append((single_file, os.path.join(dirpath, single_file)))

        if workers > 1:
            with multiprocessing.Pool(processes=workers) as pool:
                _ = pool.starmap(document_file, files)

        else:
            for arg in files:
                document_file(*arg)
