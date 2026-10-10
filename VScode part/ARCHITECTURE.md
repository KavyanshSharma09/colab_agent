# Architecture

The runtime is split into small, testable boundaries:

- `Session` owns turns and serialisable history. `EventLog` appends events as JSONL;
  `Session.open()` reconstructs history and replay never invokes tools.
- `RuntimeContext` publishes events to both an in-process `EventBus` and an optional
  persistent log.
- `ToolRegistry` describes and dispatches tools. `Permissions` gates names before
  dispatch, while `ToolExecutor` returns structured `Observation` values.
- `Model` is a provider-neutral protocol. `HttpModel` adapts the existing HTTP
  endpoint, and callers can inject a deterministic fake in tests.
- `PluginManager` owns setup/teardown and can discover `coding_agent.plugins`
  entry points.
- `analyze_python` uses `ast.parse` only; it validates workspace containment and
  never imports target code. The FastAPI app in `workspace/fastapi_analyzer`
  provides a minimal browser UI around it.
