from multiprocessing.managers import BaseManager
from typing import List

import toml

CONFIGURATION_NAME = "blackdock_configuration.toml"


def log(data: str = ""):
    print(data)


class NLPManager(BaseManager):
    pass


class Config:
    ignored_directories: List[str] = [
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
        "html"
    ]

    workers: int = 1

    @staticmethod
    def _set_values(configs: dict):
        """Load all the values from the blackdock_configuration.toml file, and use the default values for everything is not
        present in the configuration file.

        :param configs: The information deserialized from the blackdock_configuration.toml file
        :type configs: dict
        """
        # Load miscellaneous
        miscellaneous = configs.get("blackdoc", {})

        Config.workers = miscellaneous.get("workers", Config.workers)
        Config.ignored_directories = miscellaneous.get(
            "ignored_directories", Config.ignored_directories
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
        except (FileNotFoundError, toml.TomlDecodeError) as exc:
            log(f"Error {exc} while trying to locate the configuration file {configuration_paths}. "
                f"Using default configurations.")
            config_file = {}
        Config._set_values(config_file)
        return Config