"""Tool execution and observation boundaries."""
from dataclasses import dataclass
from typing import Any, Dict
from permissions import Permissions


@dataclass
class Observation:
    tool: str
    result: Any
    success: bool
    error: str | None = None
    metadata: Dict[str, Any] | None = None


class ToolExecutor:
    def __init__(self, registry: Any, permissions: Permissions | None = None) -> None:
        self.registry = registry
        self.permissions = permissions or Permissions()

    def execute(self, name: str, arguments: Dict[str, Any]) -> Observation:
        if not self.permissions.allows(name):
            return Observation(name, {"success": False, "error": "Permission denied."}, False, "Permission denied.")
        try:
            result = self.registry.execute(name, arguments)
        except Exception as exc:
            return Observation(name, {"success": False, "error": str(exc)}, False, str(exc))
        if not isinstance(result, dict):
            return Observation(name, result, True)
        success = bool(result.get("success", False))
        return Observation(name, result, success, result.get("error"))
