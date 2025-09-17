# services/ollama_client.py

import requests
import json
from typing import Any
from config.settings import OLLAMA_URL, OLLAMA_MODEL


def ollama_generate(
    prompt: str,
    model: str = OLLAMA_MODEL,
    max_tokens: int = 512,
    temperature: float = 0.0,
    timeout: int = 60,
    debug: bool = False,
) -> str:
    """
    Send prompt to Ollama and return generated text.
    Handles streaming JSON objects from Ollama's /api/generate endpoint.

    Args:
        prompt: The input prompt to send.
        model: Ollama model name.
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.
        timeout: Request timeout in seconds.
        debug: If True, prints raw chunks for debugging.

    Returns:
        The concatenated response text from Ollama.
    """
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True,
    }
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(
            url, json=payload, headers=headers, stream=True, timeout=timeout
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Return an explicit error string so the app can handle it
        return f"[Ollama Error: {str(e)}]"

    output_chunks: list[str] = []

    for line in resp.iter_lines():
        if not line:
            continue
        try:
            data = json.loads(line.decode("utf-8"))
            if debug:
                print("OLLAMA RAW:", data)

            # Ollama streams objects like {"response": "...", "done": false}
            if "response" in data:
                output_chunks.append(data["response"])
            if data.get("done", False):
                break
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

    return "".join(output_chunks).strip()
