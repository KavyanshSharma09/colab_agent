# Agent Monitor starter

This adds a local Streamlit dashboard without replacing your running Colab model server.

## 1. Copy files
Copy `dashboard.py` and `event_logger.py` into your local `rag/` folder beside `main.py`.

## 2. Install
In a second terminal:
```bash
python -m pip install streamlit pandas
```

## 3. Add four logging hooks

In `main.py`, add near the imports:
```python
from event_logger import log_event
```
Inside `agent_mode`, after the non-empty task check and before `agent.run(task)`:
```python
log_event("user_input", text=task)
```

In `agent/loop.py`, add imports:
```python
import time
from event_logger import log_event
```

Immediately before the `try:` that calls `ask_model(...)`, add:
```python
request_started = time.perf_counter()
log_event("model_request", prompt_chars=len(prompt))
```

Immediately after `response = ask_model(...)` succeeds, before the `except`, add:
```python
latency = time.perf_counter() - request_started
log_event(
    "model_response",
    text=response,
    latency_seconds=round(latency, 4),
    input_tokens=None,
    output_tokens=None,
    token_count_type="not reported by current API",
)
```

Before `registry.execute(tool_name, parameters)`:
```python
log_event("tool_call", name=tool_name, arguments=parameters)
```

Immediately after `result = registry.execute(...)`:
```python
log_event("tool_result", name=tool_name, result=result)
```

Optional: inside the loop, after printing the step heading:
```python
log_event("agent_status", message=f"Starting step {step + 1}/{MAX_STEPS}")
```

## 4. Run the UI
Keep your agent and Colab model server running. Open another terminal in `rag/`:
```bash
streamlit run dashboard.py
```
Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Important notes
- The dashboard shows the model's actual response/action JSON and tool activity, not private hidden chain-of-thought.
- The existing `/generate` endpoint returns only `{"response": "..."}`, so exact token counts are not currently available. The dashboard displays `—` rather than inventing them.
- Exact token counts require a small change to the Colab `/generate` endpoint to return tokenizer-based input/output counts, and a change to `model_client.py` to preserve that metadata. This requires restarting the FastAPI server process, but not reloading the model if the Colab runtime remains active.
- Latency measures the full local HTTP request, including Cloudflare Tunnel/network delay.
- Keep the dashboard local. It may display prompts, source code, tool output, and secrets.
