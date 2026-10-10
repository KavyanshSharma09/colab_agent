import os


# Model configuration. The tunnel URL can be replaced without changing code:
# set COLAB_URL to the current Colab/Cloudflare endpoint before starting.
COLAB_URL = os.getenv(
    "COLAB_URL",
    "https://judicial-min-click-true.trycloudflare.com",
).strip().rstrip("/")

PLACEHOLDER_URLS = {
    "https://your-new-tunnel-url.trycloudflare.com",
    "https://actual-tunnel-url.trycloudflare.com",
}

if COLAB_URL in PLACEHOLDER_URLS:
    raise RuntimeError(
        "COLAB_URL is set to a placeholder URL. Replace it with the "
        "actual URL printed by your running Colab/Cloudflare model server."
    )

MODEL_NAME = "deepseek-ai/deepseek-coder-6.7b-base"

# Generation settings
DEFAULT_MAX_NEW_TOKENS = 512
DEFAULT_TEMPERATURE = 0.4

# Agent settings
MAX_STEPS = 10

# Workspace
WORKSPACE_DIR = "workspace"