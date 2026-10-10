from tools.registry import ToolRegistry

from tools.filesystem import (
    read_file,
    write_file,
    list_files,
)

from tools.shell import (
    run_command,
)

from tools.search import (
    search_code,
)
from analyzer import analyze_python


def create_tool_registry():
    registry = ToolRegistry()

    registry.register(
        name="read_file",
        description="Read the contents of a file inside the workspace.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file relative to the workspace."
                }
            },
            "required": ["path"]
        },
        function=read_file,
    )

    registry.register(
        name="write_file",
        description="Create or overwrite a file inside the workspace.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file relative to the workspace."
                },
                "content": {
                    "type": "string",
                    "description": "Complete content to write into the file."
                }
            },
            "required": ["path", "content"]
        },
        function=write_file,
    )

    registry.register(
        name="list_files",
        description="List all files inside the workspace.",
        parameters={
            "type": "object",
            "properties": {}
        },
        function=list_files,
    )

    registry.register(
        name="run_command",
        description="Run a shell command inside the workspace.",
        parameters={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute."
                }
            },
            "required": ["command"]
        },
        function=run_command,
    )

    registry.register(
        name="search_code",
        description="Search for text inside files in the workspace.",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Text to search for."
                }
            },
            "required": ["query"]
        },
        function=search_code,
    )
    registry.register(
        name="analyze_python",
        description="Parse a Python file with AST without executing it.",
        parameters={"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        function=analyze_python,
    )

    return registry