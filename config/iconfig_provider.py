from abc import ABC, abstractmethod

class IConfigProvider(ABC):

    @abstractmethod
    def get(self, *keys: str) -> str:
        pass 

    @abstractmethod
    def _get_config(self) -> dict:
        pass
