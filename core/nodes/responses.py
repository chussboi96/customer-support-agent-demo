# core/nodes/responses.py

from typing import Dict

DEFAULT_RESPONSES: Dict[str, str] = {
    "greeting": "👋 Hi there! How can I help you today?",
    "thank_you": "🙏 You're welcome! Let me know if you need anything else.",
    "goodbye": "👋 Goodbye! Have a great day!",
    "smalltalk": "😊 I hear you! How can I assist you with your account or order?",
    "apology": "😅 No worries at all!",
    "affirmation": "✅ Got it!",
    "negation": "❌ Okay, I won’t proceed with that.",
    "confirmation": "👍 Noted! Let’s continue.",
    "unknown": "🤔 I’m not sure I understood that fully. Could you clarify?",
}

# Map dynamic / variant intent labels to canonical ones
INTENT_SYNONYMS: Dict[str, str] = {
    # Greeting variants
    "casual_greeting": "greeting",
    "hey_there": "greeting",
    "hello": "greeting",

    # Thank you variants
    "thanks": "thank_you",
    "appreciation": "thank_you",

    # Goodbye variants
    "farewell": "goodbye",
    "see_you": "goodbye",

    # Smalltalk variants
    "chitchat": "smalltalk",
    "casual_chat": "smalltalk",
}


def normalize_intent(intent: str) -> str:
    """
    Normalize dynamic or variant intents to canonical ones
    if they exist in INTENT_SYNONYMS.
    """
    if not intent:
        return intent
    return INTENT_SYNONYMS.get(intent, intent)


def get_default_response(intent: str) -> str | None:
    """
    Return a default canned response if the intent (normalized) is in DEFAULT_RESPONSES.
    Otherwise, return None.
    """
    norm = normalize_intent(intent)
    return DEFAULT_RESPONSES.get(norm)


def combine_responses(intents: list[str]) -> str | None:
    """
    If multiple lightweight intents are detected,
    normalize them and combine their canned responses into one message.
    Example: ["casual_greeting", "thanks"] → "👋 Hi there!...🙏 You're welcome!"
    """
    parts: list[str] = []
    for i in intents:
        norm = normalize_intent(i)
        if norm in DEFAULT_RESPONSES:
            parts.append(DEFAULT_RESPONSES[norm])
    if not parts:
        return None
    # join with a space; avoid duplicate adjacent responses
    # dedupe while preserving order
    seen = set()
    deduped = [p for p in parts if not (p in seen or seen.add(p))]
    return " ".join(deduped)
