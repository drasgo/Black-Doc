# Silences useless warnings
import os
import sys
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

__version__ = "1.0.0"


def get_cli_argument_parser() -> argparse.ArgumentParser:
    """
    Allows the user to pass arguments through CLI when executing the program.

    :returns: argparse.ArgumentParser - the object for retrieving the parsed arguments passed to the CLI
    """
    cli_arg_parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]",
        description="Executes the black library and generates a template docstring for every non-documented function"
        "and class of the current repository.",
    )

    group = cli_arg_parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-r',
        "--repo",
        help="If specified, the current folder is going to be recursively black-ed and docstring-ed.",
        required=False,
    )

    group.add_argument(
        "-f",
        "--file",
        help="If a single file is specified, then the 'black & doc' process is executed only on the specified "
             "(Python) file.",
        required=False,
    )

    cli_arg_parser.add_argument(
        "-b",
        "--backup",
        help="If specified, creates a backup folder of the current directory called 'blackdoc_backup' "
             "(if the backup folder already exists it overwrites it).",
        action="store_true",
        default=True,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-nb",
        "--no_black",
        help="If specified, does not perform the black operations, and only generates the docstring templates.",
        action="store_true",
        default=True,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-np",
        "--no_nlp",
        help="If specified, will not use any NLP-based tools (e.g. text segmentation) for describing a code element "
             "(Ideal for reducing the startup and documenting process time).",
        action="store_true",
        default=True,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-w",
        "--workers",
        help="Number of workers that document the files in the repository in parallel (Default=1).",
        type=int,
        required=False,
    )
    if len(sys.argv) == 1:
        cli_arg_parser.print_help(sys.stderr)
        log("\nNOTE: Either -r/--repo or -f FILE/--file FILE need to be provided.")
        sys.exit(1)
    return cli_arg_parser


def document_file(file_name: str, file_path: str, nlp_utilities) -> Tuple[bool, str]:
    """
    This method is XXX . It is a global method.

    :param file_name: XXX
    :type file_name: str
    :param file_path: XXX
    :type file_path: str
    :param nlp_utilities:
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
        log("Blacking")
        if file_path:
            black_file(file_path)
        else:
            black_repo()


def create_backup(is_backup: bool, working_dir: str):
    """
    This method is XXX . It is a global method.

    :param is_backup: XXX
    :type is_backup: bool
    :param working_dir: XXX
    :type working_dir: str
    """

    log("Backing up repository")
    if is_backup:
        if os.path.exists(working_dir + "/blackdoc_backup"):
            shutil.rmtree(working_dir + "/blackdoc_backup")
        shutil.copytree(working_dir, working_dir + "/blackdoc_backup")


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

def main():
    curr_dir = os.getcwd()
    success = []
    arg_parser = get_cli_argument_parser()
    cli_arguments = arg_parser.parse_args()

    configs = Config.load_configs(curr_dir)
    workers = cli_arguments.workers if cli_arguments.workers else configs.workers

    create_backup(cli_arguments.backup, curr_dir)

    # Initialize nlp utilities once for every worker
    nlp_utilities = None if cli_arguments.no_nlp else initialize_NLP()

    if cli_arguments.file:
        if not cli_arguments.file.endswith(".py"):
            log("Only Python files are supported!")
            exit()

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

        success.append(document_file(filename, curr_file, nlp_utilities))
        start_blacking(cli_arguments.no_black, curr_file)

    else:
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
                    files.append((single_file, os.path.join(dirpath, single_file), nlp_utilities))

        if workers > 1:
            with multiprocessing.Pool(processes=workers) as pool:
                success = pool.starmap(document_file, files)

        else:
            for arg in files:
                success.append(document_file(*arg))

        start_blacking(cli_arguments.no_black)

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

if __name__ == "__main__":
    main()