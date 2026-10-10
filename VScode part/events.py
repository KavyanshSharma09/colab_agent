"""Small, serialisable event primitives used by the harness."""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
import json
import uuid


@dataclass
class Event:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        if self.event_id is None:
            self.event_id = uuid.uuid4().hex
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Dict[str, Any]) -> "Event":
        return cls(value["type"], value.get("data", {}), value.get("timestamp", ""), value.get("event_id"))


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[Event], Any]]] = {}

    def on(self, event_type: str, handler: Callable[[Event], Any]) -> Callable[[Event], Any]:
        self._handlers.setdefault(event_type, []).append(handler)
        return handler

    def emit(self, event: Event) -> Event:
        for handler in self._handlers.get(event.type, []) + self._handlers.get("*", []):
            handler(event)
        return event


class EventLog:
    """Append-only JSONL log that can be replayed without executing actions."""
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path

    def append(self, event: Event) -> None:
        if self.path:
            from pathlib import Path
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as stream:
                stream.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
                stream.flush()

    def read(self) -> List[Event]:
        if not self.path:
            return []
        try:
            with open(self.path, encoding="utf-8") as stream:
                events = []
                for line in stream:
                    if line.strip():
                        try:
                            events.append(Event.from_dict(json.loads(line)))
                        except (json.JSONDecodeError, KeyError, TypeError):
                            continue
                return events
        except FileNotFoundError:
            return []

    def replay(self, handlers: Optional[EventBus] = None) -> List[Event]:
        """Read events in order and optionally emit them without side effects."""
        events = self.read()
        if handlers:
            for event in events:
                handlers.emit(event)
        return events
