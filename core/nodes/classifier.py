# core/nodes/classifier.py
from typing import Tuple, List
from langchain.prompts import PromptTemplate
from services.ollama_client import ollama_generate
from config.settings import OLLAMA_MODEL
import json
from core.nodes import responses as responses_module

# Prompt for static intent classification (multi-intent aware)
INTENT_PROMPT = PromptTemplate(
    input_variables=["text", "intents_list"],
    template=(
        "You are an intent classification model.\n\n"
        "User message:\n{text}\n\n"
        "Available intents (user may express more than one):\n{intents_list}, unknown\n\n"
        "Rules:\n"
        "- Choose one or more intents that match.\n"
        "- If no clear match exists, use 'unknown'.\n"
        "- If multiple intents are present, include all (the list can have 1, 2, 3, or more intents).\n"
        "- Only use intents from the provided list.\n\n"
        "Return JSON strictly in this format:\n"
        "{{\"intents\": [\"<intent1>\", \"<intent2>\", \"<intent3>\"], \"confidence\": 0.92}}\n\n"
    ),
)

# Fallback dynamic intent generator
DYNAMIC_INTENT_PROMPT = PromptTemplate(
    input_variables=["text"],
    template=(
        "You are an intent extraction model.\n\n"
        "User message:\n{text}\n\n"
        "If it does not clearly match known intents, create one or more descriptive new intent labels in snake_case.\n"
        "Keep them concise (1–2 words).\n\n"
        "Reject pure nonsense words (like 'blibberblop') and instead return ['unknown'].\n\n"
        "Return JSON strictly in this format:\n"
        "{{\"intents\": [\"<intent1>\", \"<intent2>\", \"<intent3>\"], \"confidence\": 0.8}}"
    ),
)


def _safe_parse_json_or_empty(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        return {}


def classify_intent_with_ollama(
    text: str, intents_list: List[str], confidence_threshold: float = 0.7
) -> Tuple[List[str], float]:
    """
    Multi-intent classification pipeline:
    1. Try static classification from the provided list.
    2. If low confidence or nonsense → try dynamic classification.
    3. If still no result → return ["unknown"].

    Normalizes returned intents using responses.normalize_intent.
    Handles Ollama client error strings gracefully.
    """
    intents: List[str] = []
    confidence: float = 0.0

    # --- Step 1: Try static classification ---
    prompt = INTENT_PROMPT.format(text=text, intents_list=", ".join(intents_list))
    out = ollama_generate(prompt, model=OLLAMA_MODEL, max_tokens=256, temperature=0.0)

    # Handle Ollama client-level errors (service unreachable, etc.)
    if isinstance(out, str) and out.startswith("[Ollama Error:"):
        return ["unknown"], 0.0

    parsed = _safe_parse_json_or_empty(out)
    intents_raw = parsed.get("intents") or parsed.get("intent") or []
    try:
        confidence = float(parsed.get("confidence", 0.0))
    except Exception:
        confidence = 0.0

    if isinstance(intents_raw, str):
        intents_raw = [intents_raw]
    intents = [i for i in intents_raw if i]

    # --- Step 2: Fallback if low confidence OR nonsense ---
    if (confidence < confidence_threshold) or (not intents):
        dyn_prompt = DYNAMIC_INTENT_PROMPT.format(text=text)
        out_dyn = ollama_generate(dyn_prompt, model=OLLAMA_MODEL, max_tokens=128, temperature=0.0)

        if isinstance(out_dyn, str) and out_dyn.startswith("[Ollama Error:"):
            return ["unknown"], 0.0

        parsed_dyn = _safe_parse_json_or_empty(out_dyn)
        dyn_intents = parsed_dyn.get("intents") or parsed_dyn.get("intent") or []
        try:
            dyn_conf = float(parsed_dyn.get("confidence", 0.8))
        except Exception:
            dyn_conf = 0.8

        if isinstance(dyn_intents, str):
            dyn_intents = [dyn_intents]

        # Sanity filter: reject nonsense (words without vowels or too short)
        clean_intents = [
            i for i in dyn_intents
            if i in intents_list + ["unknown"]
            or (any(v in i for v in "aeiou") and len(i) > 3)
        ]

        if clean_intents:
            normalized = [responses_module.normalize_intent(i) for i in clean_intents]
            # dedupe preserving order
            seen = set()
            normalized_unique = [x for x in normalized if not (x in seen or seen.add(x))]
            return normalized_unique, dyn_conf
        else:
            return ["unknown"], 0.5

    # Normalize intents before returning
    normalized = [responses_module.normalize_intent(i) for i in intents]
    # dedupe while preserving order
    seen = set()
    normalized_unique = [x for x in normalized if not (x in seen or seen.add(x))]

    return normalized_unique, confidence
