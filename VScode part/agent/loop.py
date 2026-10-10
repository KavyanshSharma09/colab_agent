import json

from agent.prompt import (
    build_system_prompt,
    build_model_prompt,
)
from config import MAX_STEPS
from execution import ToolExecutor
from permissions import Permissions
from models import HttpModel


def parse_model_response(response):
    """
    Extract and parse a JSON object from the model response.
    """

    cleaned = response.strip()

    # Remove markdown code fences
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    decoder = json.JSONDecoder()
    start = cleaned.find("{")

    while start != -1:
        try:
            action, _ = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            start = cleaned.find("{", start + 1)
            continue

        if isinstance(action, dict) and "action" in action:
            return action

        start = cleaned.find("{", start + 1)

    return None


def normalize_action(action):
    """
    Convert different model action formats into one
    internal format used by the agent.

    Supported model format:

    {
        "action": "write_file",
        "arguments": {
            "path": "calculator.py",
            "content": "..."
        }
    }

    Internal format:

    {
        "action": "tool",
        "arguments": {
            "name": "write_file",
            "parameters": {
                "path": "calculator.py",
                "content": "..."
            }
        }
    }
    """

    if not isinstance(action, dict):
        return None

    if "action" not in action:
        return None

    action_type = action["action"]

    # ==========================================
    # DONE
    # ==========================================

    if action_type == "done":

        arguments = action.get(
            "arguments",
            {}
        )

        if not isinstance(arguments, dict):
            arguments = {}

        return {
            "action": "done",
            "arguments": arguments
        }

    # ==========================================
    # EXPLICIT TOOL FORMAT
    # ==========================================
    #
    # {
    #     "action": "tool",
    #     "arguments": {
    #         "name": "write_file",
    #         "parameters": {}
    #     }
    # }

    if action_type == "tool":

        arguments = action.get(
            "arguments"
        )

        if not isinstance(arguments, dict):
            return None

        tool_name = arguments.get(
            "name"
        )

        parameters = arguments.get(
            "parameters",
            {}
        )

        if not tool_name:
            return None

        if not isinstance(parameters, dict):
            return None

        return {
            "action": "tool",
            "arguments": {
                "name": tool_name,
                "parameters": parameters
            }
        }

    # ==========================================
    # DIRECT TOOL FORMAT
    # ==========================================
    #
    # {
    #     "action": "write_file",
    #     "arguments": {
    #         "path": "...",
    #         "content": "..."
    #     }
    # }

    arguments = action.get(
        "arguments",
        {}
    )

    if not isinstance(arguments, dict):
        return None

    return {
        "action": "tool",
        "arguments": {
            "name": action_type,
            "parameters": arguments
        }
    }


def validate_action(action, registry):
    """
    Validate the normalized action.

    Also checks whether the requested tool
    actually exists.
    """

    if not isinstance(action, dict):
        return False

    action_type = action.get(
        "action"
    )

    # ==========================================
    # DONE
    # ==========================================

    if action_type == "done":
        return True

    # ==========================================
    # TOOL
    # ==========================================

    if action_type != "tool":
        return False

    arguments = action.get(
        "arguments"
    )

    if not isinstance(arguments, dict):
        return False

    tool_name = arguments.get(
        "name"
    )

    parameters = arguments.get(
        "parameters"
    )

    if not tool_name:
        return False

    if not isinstance(parameters, dict):
        return False

    # Check that tool actually exists
    if registry.get(tool_name) is None:
        return False

    return True


def run_agent(session, registry, model=None, executor=None):
    """
    Run the agent loop for the current session.
    """

    system_prompt = build_system_prompt(
        registry
    )

    invalid_responses = 0
    model = model or HttpModel(max_new_tokens=512, temperature=0.1)
    executor = executor or ToolExecutor(
        registry,
        Permissions.from_tools(tool["name"] for tool in registry.list_tools()),
    )
    session.state.status = "running"

    for step in range(MAX_STEPS):

        print(
            f"\n[Agent step {step + 1}/{MAX_STEPS}]"
        )

        # ==========================================
        # BUILD PROMPT
        # ==========================================

        prompt = build_model_prompt(
            system_prompt,
            session.get_events()
        )

        # ==========================================
        # ASK MODEL
        # ==========================================

        try:

            response = model.generate(prompt)

        except Exception as e:

            print(
                f"\nModel error: {e}"
            )

            session.state.status = "failed"
            session.state.last_error = str(e)
            return False

        print("\nMODEL:")
        print(response)

        # ==========================================
        # PARSE JSON
        # ==========================================

        parsed_action = parse_model_response(
            response
        )

        if parsed_action is None:

            print(
                "\nInvalid JSON from model."
            )

            invalid_responses += 1
            if invalid_responses >= 3:
                print(
                    "\nAgent stopped: model did not return a valid JSON action "
                    "after 3 attempts. Use an instruction-tuned model endpoint."
                )
                return False

            session.add_user_message(
                """
Your previous response was not valid JSON.

Return ONLY valid JSON.

Do not use markdown.

For a tool use:

{
    "action": "write_file",
    "arguments": {
        "path": "file.py",
        "content": "..."
    }
}

For completion use:

{
    "action": "done",
    "arguments": {
        "message": "Task completed."
    }
}
"""
            )

            continue

        # ==========================================
        # NORMALIZE ACTION
        # ==========================================

        action = normalize_action(
            parsed_action
        )

        if action is None:

            print(
                "\nCould not understand model action."
            )

            session.add_user_message(
                """
Your previous action could not be understood.

Use this format:

{
    "action": "tool_name",
    "arguments": {
        "parameter": "value"
    }
}

Example:

{
    "action": "write_file",
    "arguments": {
        "path": "calculator.py",
        "content": "..."
    }
}

When finished:

{
    "action": "done",
    "arguments": {
        "message": "Task completed."
    }
}
"""
            )

            continue

        invalid_responses = 0

        # ==========================================
        # VALIDATE
        # ==========================================

        if not validate_action(
            action,
            registry
        ):

            tool_name = (
                action
                .get("arguments", {})
                .get("name", "unknown")
            )

            print(
                f"\nInvalid action or unknown tool: {tool_name}"
            )

            session.add_user_message(
                f"""
The requested tool "{tool_name}" does not exist.

Only use tools listed in AVAILABLE TOOLS.
"""
            )

            continue

        session.add_model_message(response)

        # ==========================================
        # HANDLE DONE
        # ==========================================

        if action["action"] == "done":

            message = (
                action
                .get("arguments", {})
                .get(
                    "message",
                    "Task completed."
                )
            )

            print(
                f"\nDONE: {message}"
            )

            session.state.status = "completed"
            if session.turns:
                session.turns[-1].completed = True
            return True

        # ==========================================
        # HANDLE TOOL
        # ==========================================

        arguments = action["arguments"]

        tool_name = arguments["name"]

        parameters = arguments["parameters"]

        print(
            f"\nTOOL: {tool_name}"
        )

        print(
            f"ARGUMENTS: {parameters}"
        )

        # ==========================================
        # RECORD TOOL CALL
        # ==========================================

        session.add_tool_call(
            tool_name,
            parameters
        )

        # ==========================================
        # EXECUTE TOOL
        # ==========================================

        observation = executor.execute(
            tool_name,
            parameters
        )
        result = observation.result

        print(
            "\nTOOL RESULT:"
        )

        print(result)

        # ==========================================
        # RECORD TOOL RESULT
        # ==========================================

        session.add_tool_result(
            tool_name,
            result
        )
        session.state.step_count += 1

    # ==========================================
    # MAX STEPS
    # ==========================================

    print(
        "\nAgent stopped: maximum steps reached."
    )

    session.state.status = "failed"
    session.state.last_error = "maximum steps reached"
    return False