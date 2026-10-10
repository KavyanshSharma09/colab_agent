"""Explicit, conservative permission checks for tool execution."""
from dataclasses import dataclass, field
from typing import Iterable, Set


@dataclass
class Permissions:
    allowed_tools: Set[str] = field(default_factory=set)
    allow_all: bool = False

    def allows(self, name: str) -> bool:
        return self.allow_all or name in self.allowed_tools

    @classmethod
    def from_tools(cls, tools: Iterable[str]) -> "Permissions":
        return cls(set(tools))

