import requests

from config import (
    COLAB_URL,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_TEMPERATURE,
)


def ask_model(
    prompt,
    max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
    temperature=DEFAULT_TEMPERATURE,
):
    try:
        response = requests.post(
            f"{COLAB_URL}/generate",
            json={
                "prompt": prompt,
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
            },
            timeout=180,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            f"Could not reach the model service at {COLAB_URL}: {error}"
        ) from error

    if not response.ok:
        details = response.text.strip()
        suffix = f" Response: {details}" if details else ""
        hint = ""
        if response.status_code >= 500:
            hint = (
                " The model service returned a server error; restart the "
                "Colab/model backend or set COLAB_URL to a healthy endpoint."
            )
        raise RuntimeError(
            f"Model service returned HTTP {response.status_code}.{suffix}{hint}"
        )

    try:
        data = response.json()
    except ValueError as error:
        raise RuntimeError(
            "Model service returned invalid JSON."
        ) from error

    if not isinstance(data, dict) or not isinstance(data.get("response"), str):
        raise RuntimeError(
            "Model service response did not contain a string 'response' field."
        )

    return data["response"]