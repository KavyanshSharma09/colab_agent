"""Session, turn, and step state for the coding harness."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path
from events import EventLog
from runtime import RuntimeContext


@dataclass
class Step:
    number: int
    action: Dict[str, Any] = field(default_factory=dict)
    observation: Any = None


@dataclass
class Turn:
    number: int
    user_message: str
    steps: List[Step] = field(default_factory=list)
    completed: bool = False


@dataclass
class AgentState:
    status: str = "idle"
    step_count: int = 0
    last_error: Optional[str] = None


class Session:
    def __init__(self, context: Optional[RuntimeContext] = None, event_log: Optional[EventLog] = None):
        self.context = context or RuntimeContext(event_log=event_log)
        self.events: List[Dict[str, Any]] = []
        self.turns: List[Turn] = []
        self.state = AgentState()

    @classmethod
    def open(cls, path: str, context: Optional[RuntimeContext] = None) -> "Session":
        """Open a persisted JSONL event log and reconstruct a read-only history."""
        log = EventLog(path)
        session = cls(context=context or RuntimeContext(event_log=log), event_log=log)
        session.replay(log)
        return session

    def add_event(self, event_type: str, data: Dict[str, Any]) -> None:
        event = self.context.publish(event_type, **data)
        self.events.append({"type": event.type, "data": event.data, "timestamp": event.timestamp})

    def start_turn(self, content: str) -> Turn:
        turn = Turn(len(self.turns) + 1, content)
        self.turns.append(turn)
        self.add_user_message(content)
        return turn

    def add_user_message(self, content: str) -> None:
        self.add_event("user", {"content": content})

    def add_model_message(self, content: str) -> None:
        self.add_event("model", {"content": content})

    def add_tool_call(self, name: str, arguments: Dict[str, Any]) -> None:
        self.add_event("tool_call", {"name": name, "arguments": arguments})

    def add_tool_result(self, name: str, result: Any) -> None:
        self.add_event("tool_result", {"name": name, "result": result})

    def get_events(self) -> List[Dict[str, Any]]:
        return self.events

    def replay(self, event_log: EventLog) -> None:
        self.events = [{"type": e.type, "data": e.data, "timestamp": e.timestamp} for e in event_log.read()]
        self.turns.clear()
        for event in self.events:
            if event["type"] == "user":
                self.turns.append(Turn(len(self.turns) + 1, event["data"].get("content", "")))
            elif event["type"] == "tool_result" and self.turns:
                self.turns[-1].steps.append(Step(len(self.turns[-1].steps) + 1, {}, event["data"].get("result")))

    def save(self, path: str) -> str:
        """Persist the current history as JSONL, replacing any existing file."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        log = EventLog(str(target))
        target.unlink(missing_ok=True)
        for item in self.events:
            log.append(EventLogEvent(item["type"], item["data"], item["timestamp"]))
        return str(target)

    def clear(self) -> None:
        self.events.clear()
        self.turns.clear()
        self.state = AgentState()


# Kept private so save() can preserve the original event timestamp.
from events import Event as EventLogEvent
