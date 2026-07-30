from abc import ABC, abstractmethod

class AIClient(ABC):

    @abstractmethod
    def generate(self, prompt: str, **kwargs):
        raise NotImplementedError
