# core/nodes/logger.py
from typing import Dict, Any
from services.db_logger import save_log, save_feedback

def log_interaction(state: Dict[str, Any]) -> int:
    """
    Save the interaction log and return DB row id.
    """
    payload = {
        "input": state.get("user_input"),
        "intents": state.get("intents", []),
        "sentiment": state.get("sentiment"),
        "urgency": state.get("urgency"),
        "actions": state.get("action_results", []),
        "response": state.get("response_text"),
        "escalation": state.get("escalation_flag", False),
        "meta": state.get("metadata", {}),
        "feedback": state.get("feedback", None),
    }
    return save_log(payload)

def log_feedback(log_id: int, feedback: str):
    """
    Update feedback for a given log entry.
    """
    save_feedback(log_id, feedback)
