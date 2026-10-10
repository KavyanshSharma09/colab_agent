import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).resolve().parent / "agent_events.jsonl"

def log_event(event_type, **data):
    event = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "type": event_type,
        **data,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
    return event
