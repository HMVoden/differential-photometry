import importlib.resources
import logging
from pathlib import Path
from typing import Dict

import shutterbug.config.data as data
import shutterbug.config.resources as resources
import toml
from shutterbug.config.manager import ConfigDataManager


class ConfigFactory:
    files: Dict[str, Path] = {}
    name_to_class: Dict = {
        "cli": data.CLIConfig,
        "runtime": data.RuntimeConfig,
    }
    name_to_file_class: Dict = {
        "input": data.InputConfig,
        "logging": data.LoggingConfig,
        "output": data.OutputConfig,
        "photometry": data.PhotometryConfig,
    }

    def __init__(self):
        configs = importlib.resources.files(resources)
        for path in configs.iterdir():
            if path.suffix == ".toml":
                self.files[path.stem] = path

        logging.debug("Found resource files %s", self.files.items())

    def build(self, config_name: str, data: Dict = None) -> ConfigDataManager:
        if config_name in self.name_to_file_class.keys():
            return self._build_from_file(config_name)
        elif config_name in self.name_to_class.keys():
            return self._build_from_settings(config_name, data)
        else:
            return None

    def _build_from_file(self, config_name: str) -> ConfigDataManager:
        files = self.files
        ntfc = self.name_to_file_class
        if config_name in files.keys():
            data = toml.load(files[config_name])
            data_class = ntfc[config_name]
            data_class = data_class(data)
            manager = ConfigDataManager(data_class)
            logging.debug("Built configuration from file %s", config_name)
            return manager
        else:
            return None

    def _build_from_settings(
        self, config_name: str, settings: Dict = None
    ) -> ConfigDataManager:
        ntc = self.name_to_class
        data_class = ntc[config_name]
        if settings is not None:
            data_class = data_class(settings)
        else:
            data_class = data_class()
        manager = ConfigDataManager(data_class)
        logging.debug("Built configuration for non-file config %s", config_name)
        return manager
