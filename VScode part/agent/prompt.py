import json


SYSTEM_PROMPT = """
You are a coding agent running inside a local development harness.

You can interact with the user's workspace through tools.

IMPORTANT RULES:

1. Do not directly claim that you created, modified, deleted, or executed
   something unless you actually used the appropriate tool.

2. When you need to use a tool, respond with ONLY a valid JSON object.

3. Never wrap JSON in markdown code fences.

4. Never add explanations before or after the JSON.

5. Use this exact format for tool calls:

{{
    "action": "tool",
    "arguments": {{
        "name": "TOOL_NAME",
        "parameters": {{
            "PARAMETER": "VALUE"
        }}
    }}
}}

6. When the user's task is completely finished, respond with:

{{
    "action": "done",
    "arguments": {{
        "message": "Short explanation of what was completed."
    }}
}}

7. If a tool returns an error, analyze the error and decide what to do next.

8. Do not invent tool results.

9. Work only inside the provided workspace.

10. Prefer inspecting existing code before modifying it.

AVAILABLE TOOLS:

{tools}
"""


def build_system_prompt(tool_registry):
    """
    Build the system prompt using the currently registered tools.
    """

    tools = tool_registry.get_tool_schemas()

    tools_text = json.dumps(
        tools,
        indent=2
    )

    return SYSTEM_PROMPT.format(
        tools=tools_text
    )


def build_model_prompt(system_prompt, session_events):
    """
    Convert the system prompt and session events into
    a prompt that can be sent to the text-generation model.
    """

    parts = []

    parts.append(
        "SYSTEM:\n"
        + system_prompt
    )

    events = session_events
    if len(events) > 12:
        events = [session_events[0]] + session_events[-11:]

    for event in events:

        event_type = event["type"]
        data = event["data"]

        if event_type == "user":

            parts.append(
                "USER:\n"
                + data["content"]
            )

        elif event_type == "model":

            parts.append(
                "ASSISTANT:\n"
                + data["content"]
            )

        elif event_type == "tool_call":

            parts.append(
                "TOOL CALL:\n"
                + json.dumps(
                    data,
                    indent=2
                )
            )

        elif event_type == "tool_result":

            parts.append(
                "TOOL RESULT:\n"
                + json.dumps(
                    data,
                    indent=2
                )
            )

    parts.append(
        """
IMPORTANT: Generate the next agent action now.
Return exactly one JSON object and nothing else.
Do not answer the user's programming question directly.
Do not output Rust, C++, Python, Markdown, or explanations.

Required shape:
{"action":"tool","arguments":{"name":"TOOL_NAME","parameters":{}}}

When no more tool calls are needed:
{"action":"done","arguments":{"message":"Task completed."}}

ASSISTANT:
"""
    )

    return "\n\n".join(parts)