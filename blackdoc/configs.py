from multiprocessing.managers import BaseManager
from typing import List

import toml

CONFIGURATION_NAME = "blackdoc_configuration.toml"


def log(data: str = "", level: str = ""):
    """
    This method is XXX . It is a global method.

    :param data: XXX. (Default="")
    :type data: str
    :param level: XXX. (Default="")
    :type level: str
    """
    if level:
        print(f"[{level.upper()}]: {data}")
    else:
        print(data)


class NLPManager(BaseManager):
    """
    This class XXX .
    Extends class BaseManager.
    """

    pass


class Config:
    """
    This class XXX .

    Methods:
    :method load_configs:
    :method _set_values:
    """

    blacklist: List[str] = [
        # "test",
        # "tests",
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

    whitelist: List[str] = []

    backup_folder: str = "/blackdoc_backup/"

    workers: int = 3

    @staticmethod
    def _set_values(configs: dict):
        """Load all the values from the blackdoc_configuration.toml file, and use the default values for everything is not
        present in the configuration file.

        :param configs: The information deserialized from the blackdoc_configuration.toml file
        :type configs: dict
        """
        # Load miscellaneous
        miscellaneous = configs.get("blackdoc", {})

        Config.workers = miscellaneous.get("workers", Config.workers)
        Config.whitelist = miscellaneous.get("whitelist", Config.whitelist)
        Config.backup_folder = miscellaneous.get("backup_folder", Config.backup_folder)
        Config.blacklist = set(
            miscellaneous.get("blacklist", Config.blacklist) + [Config.backup_folder]
        )

    @staticmethod
    def load_configs(configuration_paths: str):
        """Deserializes the configuration file, and sets all the values into the Config class.

        :param configuration_paths: Path of the configuration file
        :type configuration_paths: str
        :returns: Type[Config] - returns the Config class, in which all the configurations are saved
        """
        try:
            with open(f"{configuration_paths}/{CONFIGURATION_NAME}", "r") as fp:
                config_file = toml.load(fp)
        except (FileNotFoundError, toml.TomlDecodeError):
            log(
                f"Error while trying to locate the configuration file {configuration_paths}. "
                f"Using default configurations.",
                level="info",
            )
            config_file = {}
        Config._set_values(config_file)
        return Config
