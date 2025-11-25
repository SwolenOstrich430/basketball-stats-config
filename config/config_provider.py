from functools import reduce
from flask import current_app

from app.service.config.iconfig_provider import IConfigProvider

class ConfigProvider(IConfigProvider):
    def __init__(self):
        pass 

    def get(self, *keys: str) -> str:
        config_val = reduce(lambda d, k: d[k], keys, self._get_config())
        
        if not config_val:
            raise KeyError(
                f"Config value not found for keys: {keys}"
            )
        
        return config_val

    
    def _get_config(self) -> dict:
        return current_app.config