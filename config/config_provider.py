from importlib import resources
from functools import reduce
import json 
from config.iconfig_provider import IConfigProvider

class ConfigProvider(IConfigProvider):
    def __init__(
        self, 
        config: dict = None, 
        package: __module__ = None, 
        config_file: str = None
    ):
        self.config = None 

        if isinstance(config, dict) and config:
            self._set_config(config)
        elif config_file is not None and package is not None:
            with resources.open_text(package, config_file) as f:
                self._set_config(json.loads(f.read()))

        if self._get_config() is None:
            raise ValueError("No valid config.")    

    def get(self, *keys: str) -> str:
        config_val = reduce(lambda d, k: d[k], keys, self._get_config())
        
        if not config_val:
            raise KeyError(
                f"Config value not found for keys: {keys}"
            )
        
        return config_val

    def _set_config(self, config: dict):
        self.config = config

    def _get_config(self) -> dict:
        return self.config