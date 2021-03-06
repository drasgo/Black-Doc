from setuptools import setup, find_packages
import os
from _version import __version__


def read_requirements(filename: str):
    """
    This method is XXX . It is a global method.

    :param filename: XXX
    :type filename: str
    :raises Exception: XXX
    """

    req = []
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("-r"):
                    req.append(line.strip())
    except Exception as ex:
        print("Could not open the file: {}".format(ex))
    return req


curr_dir = os.getcwd()
install_requires = read_requirements(os.path.abspath("./requirements.txt"))
install_requires = (
    [
        f"PythonParser@git+https://github.com/drasgo/PythonParser.git#egg=PythonParser-1.0.4"
    ]
    + [
        f"NLPUtilities@git+https://github.com/drasgo/NLPUtilities.git#egg=NLPUtilities-1.0.0"
    ]
    + [req for req in install_requires if not req.startswith("./external_packages")]
)

setup(
    name="BlackDoc",
    version=__version__,
    author="Drasgo",
    author_email="tommasocastiglione@gmail.com",
    url="https://github.com/drasgo/Black-Doc",
    description="A tool combining Black and an automatic docstring template generation for every non-documented function, "
    "following Sphinx style",
    install_requires=install_requires,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
)
