# Experimental AI Coding Agent

An experimental coding agent that runs an open-source coding model on Google
Colab and connects it to a local VS Code agent harness. Instead of relying on
a pre-hosted LLM API, this project explores what happens when the model
hosting, API layer, network bridge, agent loop, and monitoring are assembled
independently.

> This is a learning project, not a production-ready replacement for modern
> coding agents.

## Architecture

```text
Local VS Code Agent
        |
        v
Agent Harness
        |
        v
Cloudflare Tunnel
        |
        v
FastAPI Model Server (Google Colab)
        |
        v
DeepSeek Coder 6.7B
        |
        v
Generated response returned to the agent
```

### 1. Model hosting: Google Colab

DeepSeek Coder 6.7B is loaded in a Google Colab session on a Tesla T4 GPU
using 4-bit quantization. The model runs directly in the Colab runtime rather
than through a third-party inference service.

### 2. API layer: FastAPI

The model is wrapped in a FastAPI server. The server accepts prompts and
generation settings through a `/generate` endpoint and returns the generated
response as JSON.

### 3. Connectivity: Cloudflare Tunnel

Because the model server runs remotely in Colab, Cloudflare Tunnel exposes the
FastAPI service through a temporary public URL. The local agent uses that URL
as the bridge to the remote model.

### 4. Agent harness: VS Code

The local harness manages the coding workflow:

- `Agent` coordinates the agent loop.
- `HttpModel`/`model_client.py` sends requests to the remote model.
- The tool registry dispatches filesystem, search, shell, and analysis tools.
- Permissions control which tools may be used.
- Session and event components provide structured history and runtime events.

The command-line entry point in `main.py` provides:

1. Agent mode for coding tasks.
2. General chat mode for direct model requests.
3. An exit option.

### 5. Monitoring and observability

The project includes a local Streamlit dashboard and JSONL event logging for
inspecting prompts, model responses, request history, latency, and tool
activity. Monitoring is intended to make the communication between the local
harness and remote model easier to understand.

## Setup

### Configure the model endpoint

Set `COLAB_URL` to the current URL printed by the running Cloudflare Tunnel:

```powershell
$env:COLAB_URL = "https://your-tunnel-url.trycloudflare.com"
```

The local client sends requests to:

```text
https://your-tunnel-url.trycloudflare.com/generate
```

The tunnel URL is temporary and may change whenever the Colab runtime or
tunnel restarts.

### Install dependencies

From this directory, install the dependencies required by the harness:

```powershell
python -m pip install requests
```

To use the monitoring dashboard:

```powershell
python -m pip install streamlit pandas
```

### Run the agent

```powershell
python main.py
```

Choose **Agent Mode** to run coding tasks or **General Chat** to send a direct
prompt to the model.

### Run the dashboard

Keep the agent and Colab model server available, then start the dashboard in a
separate terminal:

```powershell
streamlit run dashboard.py
```

Open the local URL printed by Streamlit, usually
`http://localhost:8501`.

## Monitoring notes

- The dashboard displays model responses and tool activity, not private hidden
  chain-of-thought.
- The current `/generate` response contains the generated text but does not
  provide exact tokenizer-based input and output token counts.
- Latency includes the local HTTP request and Cloudflare Tunnel network delay.
- Keep the dashboard local because prompts, source code, tool output, and
  environment details may be visible in the logs.

## Limitations

### Colab session limits

The free Colab tier is not a persistent inference service. When the runtime
disconnects or reaches its session limit, the model and API become unavailable.

### Tunnel latency and reliability

Requests travel from the local machine to Colab through the Cloudflare Tunnel
and then return with the model response. This additional network overhead can
make coding tasks slower and less predictable. The public URL can also change
when the tunnel restarts.

### Model capability

DeepSeek Coder 6.7B Instruct is considerably smaller than the models used by
many modern coding agents. A better harness cannot completely remove the
model's limitations in reasoning, coding accuracy, and complex task handling.

### Agent reliability

An agent loop alone does not make a reliable coding agent. Context management,
tool execution, error recovery, code validation, and iterative problem-solving
all introduce additional engineering challenges.

### Temporary infrastructure

The complete system depends on the Colab runtime, the tunnel, the network
connection, and the local harness being available at the same time.

## AI-assisted development

A substantial portion of this experiment was developed with AI assistance.
The goal was not to manually write every line, but to understand the
architecture, integrate the components, troubleshoot connectivity, and observe
how the complete system behaves in practice.

The learning comes from understanding how the pieces fit together and working
through the problems that appear during integration.

## What this experiment demonstrates

An AI coding agent is more than an LLM connected to an API. The model is only
one component. The harness, tool execution, context management,
infrastructure, latency, observability, and reliability all influence the
final experience.

This project is a small experiment for understanding that engineering by
building a simplified version of the workflow:

> Keep learning. Keep experimenting. Keep building.

## License and attribution

This repository is an experimental implementation assembled for educational
purposes. Review the licenses of the model, harness code, and dependencies
before redistributing or deploying the project.

#AI #AIAgents #DeepSeek #LLM #Python #FastAPI #GenerativeAI #VSCode #OpenSourceAI
