from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, messages: list[dict[str, str]]) -> str | None:
        """Generate text from chat-style messages."""
        raise NotImplementedError