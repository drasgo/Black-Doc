import concurrent
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from typing import Tuple, Union, List

from blackdoc.isort import isort_file

# Silences useless warnings
warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import argparse

import shutil

from nlputilities.nlp import NLPUtilities

from blackdoc.black import black_file, black_repo
from blackdoc.configs import log, Config, NLPManager
from blackdoc.docstring import DocumentFile

__version__ = "1.1.1"


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
        "-r",
        "--repo",
        help="If specified, the current folder is going to be recursively black-ed and docstring-ed.",
        action="store_true",
        default=False,
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
        "--no_backup",
        help="If specified, it does not create a backup folder of the current directory called 'blackdoc_backup' "
        "(NOTE: if the backup is created and 'blackdoc_backup' already exists, it overwrites it).",
        action="store_true",
        default=False,
        required=False,
    )

    cli_arg_parser.add_argument(
        "--no_black",
        help="If specified, does not perform the black operation. More info at: https://github.com/psf/black .",
        action="store_true",
        default=False,
        required=False,
    )

    cli_arg_parser.add_argument(
        "--no_isort",
        help="If specified, does not perform the isort operations, More info at: https://github.com/PyCQA/isort .",
        action="store_true",
        default=False,
        required=False,
    )

    cli_arg_parser.add_argument(
        "--use_nlp",
        help="If specified, it will use NLP-based tools (e.g. text segmentation) for describing the code elements in the "
        "docstrings. (Experimental. Increases startup time and overall processing time).",
        action="store_true",
        default=False,
        required=False,
    )

    cli_arg_parser.add_argument(
        "-w",
        "--workers",
        help="Number of workers that document the files in the repository in parallel (Default=3).",
        type=int,
        required=False,
    )
    if len(sys.argv) == 1:
        cli_arg_parser.print_help(sys.stderr)
        log("\nNOTE: Either -r/--repo or -f FILE/--file FILE need to be provided.")
        sys.exit(1)
    return cli_arg_parser


def document_file(nlp_utilities, file_path: str) -> Tuple[bool, str]:
    """
    This method is XXX . It is a global method.

    :param file_path: XXX
    :type file_path: str
    :param nlp_utilities:
    :returns: Tuple[bool, str] - XXX
    """
    file_name = file_path.split("/")[-1]
    log(f"Documenting {file_name}")
    docs = DocumentFile(file_name, file_path, nlp_utilities)
    return docs.document_file(), file_path


def start_blacking(no_black: bool, file_path: str = ""):
    """
    This method is XXX . It is a global method.

    :param no_black: XXX
    :type no_black: bool
    :param file_path: XXX. (Default="")
    :type file_path: str
    """

    if not no_black:
        log("\nBlacking")
        if file_path:
            black_file(file_path)
        else:
            black_repo()


def start_isorting(no_isort: bool, file_paths: Union[str, List[str]] = ""):
    """
    This method is XXX . It is a global method.

    :param no_isort: XXX
    :type no_isort: bool
    :param file_paths: XXX. (Default="")
    :type file_paths: Union[str, List[str]]
    """

    if not no_isort:
        log("\nISorting")
        file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        for path in file_paths:
            isort_file(path)


def create_backup(is_backup: bool, working_dir: str):
    """
    This method is XXX . It is a global method.

    :param is_backup: XXX
    :type is_backup: bool
    :param working_dir: XXX
    :type working_dir: str
    """

    log("\nBacking up repository")
    if is_backup:
        if os.path.exists(working_dir + Config.backup_folder):
            shutil.rmtree(working_dir + Config.backup_folder)
        shutil.copytree(working_dir, working_dir + Config.backup_folder)


def initialize_NLP(is_nlp: bool):
    """
    This method is XXX . It is a global method.
    """
    if not is_nlp:
        return None
    log("\nLoading NLP-based tools")
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


def update_gitignore(backup: bool, curr_dir: str):
    """
    This method is XXX . It is a global method.

    :param backup: XXX
    :type backup: bool
    :param curr_dir: XXX
    :type curr_dir: str
    """

    if backup:
        gitignore_file = os.path.join(curr_dir, ".gitignore")
        backup_folder = Config.backup_folder[1:]

        if os.path.exists(gitignore_file):

            with open(gitignore_file, "r") as fp:
                ignored_elements = fp.readlines()

            if not any(backup_folder in element for element in ignored_elements):
                log(f"\nUpdating .gitignore to ignore {Config.backup_folder}.")
                ignored_elements.append(backup_folder)

                with open(gitignore_file, "w") as fp:
                    fp.writelines(ignored_elements)


def main():
    """
    This method is XXX . It is a global method.

    :raises Exception: XXX
    """

    curr_dir = os.getcwd()
    success = []
    arg_parser = get_cli_argument_parser()
    cli_arguments = arg_parser.parse_args()

    configs = Config.load_configs(curr_dir)
    workers = cli_arguments.workers if cli_arguments.workers else configs.workers

    update_gitignore(not cli_arguments.no_backup, curr_dir)
    create_backup(not cli_arguments.no_backup, curr_dir)

    # Initialize nlp utilities once for every worker
    nlp_utilities = initialize_NLP(cli_arguments.use_nlp)

    if cli_arguments.file:
        if not cli_arguments.file.endswith(".py"):
            log("\nOnly Python files are supported!", "error")
            exit()

        curr_file = os.path.join(curr_dir, cli_arguments.file)

        success.append(document_file(nlp_utilities, curr_file))
        start_blacking(cli_arguments.no_black, curr_file)
        start_isorting(cli_arguments.no_isort, curr_file)

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

            if not configs.whitelist or (
                configs.whitelist
                and any(
                    subfolder == allowed
                    for subfolder in relative_path.split("/")
                    for allowed in configs.whitelist
                )
            ):
                for single_file in [file for file in filenames if file.endswith(".py")]:
                    files.append(os.path.join(dirpath, single_file))

        if workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                jobs = {
                    executor.submit(document_file, nlp_utilities, file_path): file_path
                    for file_path in files
                }

            for future in concurrent.futures.as_completed(jobs):
                path = jobs[future]
                try:
                    status, _ = future.result()
                except Exception:
                    status = False
                success.append((status, path))

        else:
            for file in files:
                success.append(document_file(nlp_utilities, file))

        start_blacking(cli_arguments.no_black)
        start_isorting(cli_arguments.no_isort, files)

    documented = 0
    non_documented = []
    for status, path in success:
        if status:
            documented += 1
        else:
            non_documented.append(path)

    log(f"\nSuccessfully documented {documented} out of {len(success)} files found")
    if non_documented:
        log("\nProblem occured documenting the following files:", "warning")
        for file in non_documented:
            log(f"- {file}")


if __name__ == "__main__":
    main()
