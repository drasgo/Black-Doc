import subprocess

from blackdoc.configs import log, Config


def black_repo():
    """
    This method is XXX . It is a global method.
    """

    temp = subprocess.run(
        f'black --extend-exclude="{Config.backup_folder}" .',
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        shell=True,
    )
    report = temp.stderr.decode()
    if report and not report.startswith("All done!"):
        log(f"Error blacking the repository: {report}!")
    else:
        log(f"Finished formatting the repository!\n{report}")


def black_file(file_path: str):
    """
    This method is XXX . It is a global method.

    :param file_path: XXX
    :type file_path: str
    """

    temp = subprocess.run(
        "black " + file_path,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        shell=True,
    )
    report = temp.stderr.decode()
    if report and not report.startswith("All done!"):
        log(f"Error blacking the file {file_path}: {report}")
    else:
        log(f"Finished formatting the file {file_path}!")
