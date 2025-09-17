from typing import Dict, Any

def create_escalation_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    # Structured payload to handoff to humans / CRM
    payload = {
        "user_input": state["user_input"],
        "intents": state.get("intents", []),
        "sentiment": state.get("sentiment"),
        "urgency": state.get("urgency"),
        "action_results": state.get("action_results"),
        "notes": "Auto-escalation due to low confidence or unhandled tools."
    }
    return payload
