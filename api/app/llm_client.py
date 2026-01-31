import os
import requests

OLLAMA_URL = os.environ.get("EDGELAB_OLLAMA_URL", "http://ollama:11434")

def generate_feedback(prompt: str, model: str | None = None) -> str:
    model = model or os.environ.get("EDGELAB_OLLAMA_MODEL", "deepseek-coder:6.7b")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except requests.RequestException as e:
        raise RuntimeError(f"Ollama request failed: {e}")
