from abc import ABC, abstractmethod

class IConfigProvider(ABC):

    @abstractmethod
    def get(self, *keys: str) -> str:
        pass 
    
    @abstractmethod
    def _set_config(self, config: dict = None, config_file: str = None) -> dict:
        pass

    @abstractmethod
    def _get_config(self) -> dict:
        pass
