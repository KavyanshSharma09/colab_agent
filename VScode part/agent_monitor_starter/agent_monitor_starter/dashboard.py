import json
from pathlib import Path
import pandas as pd
import streamlit as st

LOG_PATH = Path(__file__).resolve().parent / "agent_events.jsonl"
st.set_page_config(page_title="Agent Monitor", page_icon="🧠", layout="wide")
st.title("🧠 Coding Agent Monitor")
st.caption("Live terminal input, model responses, tool actions, latency and token usage.")

def read_events():
    if not LOG_PATH.exists():
        return []
    rows = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows

@st.fragment(run_every=2)
def dashboard():
    events = read_events()
    if not events:
        st.info("No events yet. Add the logging hooks from README.md, then submit a task in your agent terminal.")
        st.code(str(LOG_PATH))
        return

    model_calls = [e for e in events if e.get("type") == "model_response"]
    user_inputs = [e for e in events if e.get("type") == "user_input"]
    tool_calls = [e for e in events if e.get("type") == "tool_call"]
    latencies = [float(e["latency_seconds"]) for e in model_calls if e.get("latency_seconds") is not None]
    in_tokens = sum(int(e.get("input_tokens") or 0) for e in model_calls)
    out_tokens = sum(int(e.get("output_tokens") or 0) for e in model_calls)

    cols = st.columns(5)
    cols[0].metric("Tasks", len(user_inputs))
    cols[1].metric("Model calls", len(model_calls))
    cols[2].metric("Tool calls", len(tool_calls))
    cols[3].metric("Avg latency", f"{sum(latencies)/len(latencies):.2f}s" if latencies else "—")
    cols[4].metric("Tokens in / out", f"{in_tokens:,} / {out_tokens:,}" if model_calls else "—")
    st.caption("Token counts are exact only if your model API supplies them. Missing counts are not estimated.")

    left, right = st.columns(2)
    with left:
        st.subheader("Latest terminal input")
        latest = next((e for e in reversed(events) if e.get("type") == "user_input"), None)
        st.code(latest.get("text", "") if latest else "No task logged", language="text")
        st.subheader("Latest model response")
        latest = next((e for e in reversed(events) if e.get("type") == "model_response"), None)
        if latest:
            st.caption(f"Latency: {latest.get('latency_seconds', '—')} s · Input tokens: {latest.get('input_tokens', '—')} · Output tokens: {latest.get('output_tokens', '—')}")
            st.code(latest.get("text", ""), language="json")
        else:
            st.write("No model response logged yet.")

    with right:
        st.subheader("Live activity timeline")
        for e in reversed(events[-40:]):
            kind = e.get("type", "event")
            if kind == "user_input":
                title, body = "👤 Terminal input", e.get("text", "")
            elif kind == "model_request":
                title, body = "🌐 Model request", f"Prompt characters: {e.get('prompt_chars', '—')}"
            elif kind == "model_response":
                title, body = "🧠 Model response", e.get("text", "")
            elif kind == "tool_call":
                title, body = f"🛠️ Tool call: {e.get('name', '')}", json.dumps(e.get("arguments", {}), indent=2, ensure_ascii=False)
            elif kind == "tool_result":
                title, body = f"📦 Tool result: {e.get('name', '')}", json.dumps(e.get("result", {}), indent=2, ensure_ascii=False)
            elif kind == "agent_status":
                title, body = "📍 Agent status", e.get("message", "")
            else:
                title, body = kind, json.dumps(e, ensure_ascii=False)
            with st.expander(f"{e.get('timestamp', '')} · {title}"):
                st.code(str(body), language="text")

    st.subheader("Event table")
    table = [{
        "time": e.get("timestamp"),
        "event": e.get("type"),
        "latency_s": e.get("latency_seconds"),
        "input_tokens": e.get("input_tokens"),
        "output_tokens": e.get("output_tokens"),
        "tool": e.get("name"),
    } for e in reversed(events)]
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)

dashboard()
