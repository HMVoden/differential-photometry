import importlib.resources
import logging
from typing import Any, Dict

import toml

import config.resources as resources

__config_files = {}
__config_runtime = {}

# This is just a singleton updating two dicts, I don't see
# any reason to make this a class.


def init_configuration():
    files = importlib.resources.files(resources)

    toml_resources = [x for x in files.iterdir() if x.suffix == ".toml"]

    for f in toml_resources:
        data = toml.load(f)
        logging.debug("Loaded configuration file %s", f.stem)
        __config_files[f.stem] = data


def get_file_configuration(config_name: str) -> Dict:
    return load_from_config(config_name=config_name,
                            config_dict=__config_files)


def get_runtime_configuration(config_name: str) -> Any:
    return load_from_config(config_name=config_name,
                            config_dict=__config_runtime)


def add_configuration(config_name: str, config_data: Any) -> bool:
    if config_name in __config_runtime.keys():
        logging.warning("Rejected attempt to overwrite configuration %s",
                        config_name)
        return False
    else:
        __config_runtime[config_name] = config_data
        return True


def load_from_config(config_name: str, config_dict: Dict) -> Any:
    try:
        return config_dict[config_name]
    except KeyError:
        logging.warning(
            "Unable to load configuration from %s, not found in configuration",
            config_name)
        return None
