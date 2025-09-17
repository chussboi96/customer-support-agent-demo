from typing import TypedDict, List, Optional, Dict, Any

class SupportAgentState(TypedDict, total=False):
    user_input: str
    normalized_input: str
    intents: List[str]
    sentiment: str
    urgency: str
    action_results: List[Dict[str, Any]]
    response_text: str
    confidence_score: float
    escalation_flag: bool
    log: List[Dict[str, Any]]
    metadata: Dict[str, Any]
