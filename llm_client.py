# llm_client.py
import requests
from config.settings import LLM_COMPLETION_PATH

def call_llm(prompt, max_tokens=512, temperature=0.0):
    """
    Basic POST to: {LLM_COMPLETION_PATH}
    Adjust the payload keys if your server expects something different.
    """
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        resp = requests.post(LLM_COMPLETION_PATH, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        # try common response shapes:
        if "choices" in data and len(data["choices"])>0:
            return data["choices"][0].get("text") or data["choices"][0].get("message", {}).get("content")
        # Ollama style:
        if "response" in data:
            return data["response"]
        # fallback to raw text
        return resp.text
    except Exception as e:
        return f"[LLM call error] {e}"
