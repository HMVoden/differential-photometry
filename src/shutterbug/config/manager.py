import logging
from typing import Any

from shutterbug.config.data import ConfigData


class ConfigDataManager:
    data: ConfigData

    def __init__(self, config_data):
        self.data = config_data

    def get(self, config_name: str) -> Any:
        return getattr(self.data, config_name, None)

    def update(self, config_name: str, config_data: Any) -> bool:
        try:
            setattr(self.data, config_name, config_data)
            return True
        except:
            return False

    def add(self, config_name: str, config_data: Any) -> bool:
        if getattr(self.data, config_name, None) is not None:
            logging.warning("Tried to add %s, but already existed.", config_name)
            return False
        else:
            return self.update(config_name, config_data)

    def delete(self, config_name: str) -> bool:
        try:
            delattr(self.data, config_name)
            return True
        except:
            return False

    def __repr__(self):
        return self.data.__repr__()

    def __str__(self):
        return self.data.__str__()
