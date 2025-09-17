# core/nodes/preprocessing.py
import re
from typing import Dict, Any

def normalize(user_input: str) -> str:
    text = user_input.strip()
    # Basic cleaning
    text = re.sub(r"\s+", " ", text)
    # keep punctuation for NER but normalize whitespace
    return text

def extract_entities(normalized_text: str) -> Dict[str, Any]:
    """
    Minimal entity extraction: looks for order-like tokens / emails / dates.
    Returns dictionary with possible keys like 'order_id' and 'email'.
    """
    entities = {}
    m = re.search(r"\bORD[\d-]*\b", normalized_text, re.IGNORECASE)
    if m:
        entities["order_id"] = m.group(0).upper()
    m2 = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", normalized_text)
    if m2:
        entities["email"] = m2.group(0).lower()
    return entities
