import subprocess

from blackdoc.configs import log


def black_repo():
    temp = subprocess.run(
        "black .", stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, shell=True
    )
    if temp.stderr and not temp.stderr.startswith(b"All done!"):
        log(f"Error blacking the repository: {temp.stderr}!")
    else:
        log(f"Finished formatting the repository!\n{temp.stderr}")


def black_file(file_path: str):
    temp = subprocess.run(
        "black " + file_path,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        shell=True,
    )
    if temp.stderr and not temp.stderr.startswith(b"All done!"):
        log(f"Error blacking the file {file_path}")
    else:
        log(f"Finished formatting the file {file_path}!")
