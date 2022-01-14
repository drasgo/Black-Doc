from setuptools import setup, find_packages
import os
from _version import __version__


def read_requirements(filename: str):
    req = []
    try:
        with open(filename, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("-r"):
                    req.append(line.strip())
    except Exception as ex:
        print("Could not open the file: {}".format(ex))
    return req


install_requires = read_requirements(os.path.abspath("./requirements.txt"))


setup(
    name="BlackDoc",
    version=__version__,
    author="Drasgo",
    author_email="tommasocastiglione@gmail.com",
    url="https://github.com/drasgo",
    description="A tool combining Black and an automatic docstring template generation for every non-documented function"
    ", following Sphinx style",
    install_requires=install_requires,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Proprietary",
        "Operating System :: Linux",
    ],
)
