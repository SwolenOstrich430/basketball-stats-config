from functools import reduce
from config.iconfig_provider import IConfigProvider

class ConfigProvider(IConfigProvider):
    def __init__(self, config: dict):
        self._set_config(config)
        pass 

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
        return current_app.config