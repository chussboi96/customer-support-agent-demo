# core/nodes/response.py
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from services.ollama_client import ollama_generate
from config.settings import OLLAMA_MODEL
import json

RESPONSE_PROMPT = PromptTemplate(
    input_variables=["user", "intents", "action_results", "sentiment", "urgency"],
    template=(
        "You are a helpful and empathetic customer support assistant.\n"
        "User message:\n{user}\n\n"
        "Detected intents: {intents}\n"
        "Action results (JSON): {action_results}\n"
        "Sentiment: {sentiment} | Urgency: {urgency}\n\n"
        "Produce a concise, friendly response tailored to the sentiment and urgency, "
        "referencing any action results when appropriate. If escalation_flag is present, give a short handover sentence.\n"
    )
)


def _serialize_action_results(action_results: List[Dict[str, Any]]) -> str:
    try:
        return json.dumps(action_results, ensure_ascii=False)
    except Exception:
        return str(action_results)


def ollama_generate_response(user: str, intents: List[str], action_results: List[Dict[str, Any]], sentiment: str, urgency: str) -> str:
    """
    Request a generated response from Ollama. If Ollama returns an error string,
    provide a safe fallback message that asks for clarification and escalates.
    """
    prompt = RESPONSE_PROMPT.format(
        user=user,
        intents=", ".join(intents),
        action_results=_serialize_action_results(action_results),
        sentiment=sentiment,
        urgency=urgency
    )
    out = ollama_generate(prompt, model=OLLAMA_MODEL, max_tokens=300, temperature=0.2)

    # Ollama client might return a service error string
    if isinstance(out, str) and out.startswith("[Ollama Error:"):
        # Provide a short, safe fallback message
        return "Sorry — I'm temporarily unable to generate a detailed reply. I've escalated this to a human agent who will follow up shortly."

    return out.strip()
