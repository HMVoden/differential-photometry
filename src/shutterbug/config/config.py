import logging
from typing import Dict

from shutterbug.config.factory import ConfigFactory
from shutterbug.config.manager import ConfigDataManager


class Singleton:
    _instance = None  # Keep instance reference

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


class ConfigDirector(Singleton):
    factory: ConfigFactory = ConfigFactory()
    built_config: Dict = {}

    def __init__(self, **cli_settings):
        self.factory = ConfigFactory()
        cli = self.factory.build("cli", cli_settings)
        self.built_config["cli"] = cli

    def get(self, config_name: str) -> ConfigDataManager:
        config = self.built_config
        to_return = None
        if config_name in config.keys():
            to_return = config[config_name]
        else:
            to_return = self.factory.build(config_name)
        if to_return is None:
            logging.error("Could not get config for %s", config_name)
        return to_return

    def clear_runtime(self) -> bool:
        """removes runtime configuration if any

        Returns
        -------
        bool
            Confirmation that runtime configuration does not exist

        """
        config = self.built_config
        if "runtime" in config.keys():
            config.pop("runtime", None)
            return True
        else:
            return True
