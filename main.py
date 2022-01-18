# Silences useless warnings
import os
import warnings
from typing import Tuple

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import argparse
import multiprocessing

import shutil

from nlputilities.nlp import NLPUtilities

from blackdoc.black import black_file, black_repo
from blackdoc.configs import log, Config, NLPManager
from blackdoc.docstring import DocumentFile

__version__ = "0.8.0"


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
        help="If specified, creates a backup folder called 'blackdoc_backup' (if the folder backup does not exist, otherwise it exits) "
        "(Default True).",
        action="store_true",
        default=True,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-nb",
        "--no_black",
        help="If specified, does not perform the black operations, and only generates the docstring templates (Default False).",
        action="store_true",
        default=True,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-np",
        "--no_nlp",
        help="If specified, will not use any NLP-based tools (e.g. text segmentation) for describing a code element "
             "(Ideal for reducing the startup and documenting process time) (Default False).",
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


def document_file(file_name: str, file_path: str) -> Tuple[bool, str]:
    """
    This method is XXX . It is a global method.

    :param file_name: XXX
    :type file_name: str
    :param file_path: XXX
    :type file_path: str
    :returns: Tuple[bool, str] - XXX
    """

    log(f"Documenting {file_name}")
    docs = DocumentFile(file_name, file_path, nlp_utilities)
    return docs.document_file(), file_path


def start_blacking(no_black: bool, file_path: str=""):
    """
    This method is XXX . It is a global method.

    :param no_black: XXX
    :type no_black: bool
    :param file_path: XXX. (Default="")
    :type file_path: str
    """

    if not no_black:
        print("Blacking")
        if file_path:
            black_file(file_path)
        else:
            black_repo()


def create_backup(is_backup: bool):
    """
    This method is XXX . It is a global method.

    :param is_backup: XXX
    :type is_backup: bool
    """

    log("Backing up repository")
    if is_backup:
        if os.path.exists(curr_dir + "/blackdoc_backup"):
            shutil.rmtree(curr_dir + "/blackdoc_backup")
        shutil.copytree(curr_dir, curr_dir + "/blackdoc_backup")


def initialize_NLP():
    """
    This method is XXX . It is a global method.
    """

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
    success = []
    curr_dir = os.getcwd()
    arg_parser = get_cli_argument_parser()
    cli_arguments = arg_parser.parse_args()

    configs = Config.load_configs(curr_dir)
    workers = cli_arguments.workers if cli_arguments.workers else configs.workers

    create_backup(cli_arguments.backup)

    # Initialize nlp utilities once for every worker
    nlp_utilities = None if cli_arguments.no_nlp else initialize_NLP()

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

        start_blacking(cli_arguments.no_black, curr_file)
        success.append(document_file(filename, curr_file))

    else:
        start_blacking(cli_arguments.no_black)

        files = []
        for dirpath, dirnames, filenames in os.walk(curr_dir, topdown=True):
            relative_path = dirpath.replace(curr_dir, "")
            if any(
                    subfolder == ignored
                    for subfolder in relative_path.split("/")
                    for ignored in configs.blacklist
            ):
                continue

            if not configs.whitelist or \
                    (configs.whitelist and any(subfolder == allowed
                                               for subfolder in relative_path.split("/")
                                               for allowed in configs.whitelist
                                               )):
                for single_file in [file for file in filenames if file.endswith(".py")]:
                    files.append((single_file, os.path.join(dirpath, single_file)))

        if workers > 1:
            with multiprocessing.Pool(processes=workers) as pool:
                success = pool.starmap(document_file, files)

        else:
            for arg in files:
                success.append(document_file(*arg))

    documented = 0
    non_documented = []
    for status, path in success:
        if status:
            documented += 1
        else:
            non_documented.append(path)

    log(f"Successfully documented {documented} out of {len(success)} files found")
    if non_documented:
        log("Problem occured documenting the following files:")
        for file in non_documented:
            log(f"- {file}")
