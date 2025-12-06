from abc import ABC, abstractmethod

class ISecretProvider(ABC):
    
    @abstractmethod
    def get_secret(self, secret_key: str) -> str:
        pass