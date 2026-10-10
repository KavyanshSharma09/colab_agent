"""Runtime services shared by sessions, tools, plugins, and the agent loop."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from events import Event, EventBus, EventLog


@dataclass
class RuntimeContext:
    workspace: str = "workspace"
    event_bus: EventBus = field(default_factory=EventBus)
    event_log: Optional[EventLog] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def publish(self, event_type: str, **data: Any) -> Event:
        event = Event(event_type, data)
        self.event_bus.emit(event)
        if self.event_log:
            self.event_log.append(event)
        return event

