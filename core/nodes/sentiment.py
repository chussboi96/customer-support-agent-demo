# core/nodes/sentiment.py
from typing import Tuple
from services.ollama_client import ollama_generate
from config.settings import OLLAMA_MODEL
import json

SENTIMENT_PROMPT = (
    "Classify the sentiment and urgency of the following message.\n\n"
    "Message: '''{text}'''\n\n"
    "Return JSON: {{\"sentiment\": \"positive|neutral|negative\", \"urgency\": \"low|medium|high\"}}"
)


def analyze_sentiment_with_ollama(text: str) -> Tuple[str, str]:
    prompt = SENTIMENT_PROMPT.format(text=text)
    out = ollama_generate(prompt, model=OLLAMA_MODEL, max_tokens=64, temperature=0.0)

    if isinstance(out, str) and out.startswith("[Ollama Error:"):
        # fallback heuristic
        lower = text.lower()
        sentiment = "negative" if any(w in lower for w in ["not", "never", "hate", "angry", "frustrat"]) else "neutral"
        urgency = "high" if any(w in lower for w in ["now", "immediately", "asap", "urgent"]) else "low"
        return sentiment, urgency

    try:
        parsed = json.loads(out)
        return parsed.get("sentiment", "neutral"), parsed.get("urgency", "low")
    except Exception:
        # naive fallback
        lower = text.lower()
        sentiment = "negative" if any(w in lower for w in ["not", "never", "hate", "angry", "frustrat"]) else "neutral"
        urgency = "high" if any(w in lower for w in ["now", "immediately", "asap", "urgent"]) else "low"
        return sentiment, urgency
