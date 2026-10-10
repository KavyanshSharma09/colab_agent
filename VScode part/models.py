"""Model abstraction with a compatibility adapter for the existing endpoint."""
from dataclasses import dataclass
from typing import Any, Dict, Protocol
from model_client import ask_model


class Model(Protocol):
    def generate(self, prompt: str, **options: Any) -> str: ...


@dataclass
class HttpModel:
    max_new_tokens: int = 512
    temperature: float = 0.1

    def generate(self, prompt: str, **options: Any) -> str:
        settings: Dict[str, Any] = {
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
        }
        settings.update(options)
        return ask_model(prompt, **settings)

