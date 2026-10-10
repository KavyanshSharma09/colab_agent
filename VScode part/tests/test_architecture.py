import json

from analyzer import analyze_python
from events import Event, EventLog
from execution import ToolExecutor
from permissions import Permissions
from session import Session


class Registry:
    def execute(self, name, arguments):
        return {"success": True, "result": arguments}


def test_jsonl_session_round_trip(tmp_path):
    path = tmp_path / "session.jsonl"
    session = Session(event_log=EventLog(str(path)))
    session.start_turn("inspect")
    session.add_model_message("done")
    assert path.exists()
    restored = Session.open(str(path))
    assert [event["type"] for event in restored.get_events()] == ["user", "model"]
    assert restored.turns[0].user_message == "inspect"


def test_executor_denies_unlisted_tool():
    observation = ToolExecutor(Registry(), Permissions()).execute("secret", {})
    assert not observation.success
    assert observation.error == "Permission denied."


def test_analyzer_is_ast_only(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "example.py").write_text("from os import path\n\ndef f(): pass\n", encoding="utf-8")
    result = analyze_python("example.py", str(workspace))
    assert result["valid"] is True
    assert "os" in result["imports"]
    assert "f" in result["functions"]
