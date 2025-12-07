from importlib import resources
from functools import reduce
import json 
from basketball_stats_config.config.iconfig_provider import IConfigProvider
from basketball_stats_config.secret.isecret_provider import ISecretProvider

SECRET_PREFIX = "secret://"

class ConfigProvider(IConfigProvider):
    def __init__(
        self, 
        config: dict = None, 
        package: __module__ = None, 
        config_file: str = None, 
        secret_provider: ISecretProvider = None
    ):
        assert isinstance(secret_provider, ISecretProvider)
        self.secret_provider = secret_provider
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
    
    def decorate_secrets(self, config_val: str|list|dict) -> str|list|dict:
        if isinstance(config_val, str) and self.is_secret(config_val):
            return self.secret_provider.get_secret(config_val)
        elif isinstance(config_val, list):
            return map(self.decorate_secrets, config_val)
        elif isinstance(config_val, dict):
            for key, val in dict.items():
                config_val[key] = self.decorate_secrets(val)

        return config_val


    def is_secret(self, value: str) -> bool:
        return isinstance(value, str) and value.startswith(
            SECRET_PREFIX
        )

    def _set_config(self, config: dict):
        self.config = self.decorate_secrets(config)

    def _get_config(self) -> dict:
        return self.config