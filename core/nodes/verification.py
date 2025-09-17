# core/nodes/verification.py

from typing import List, Dict
from core.nodes import responses


def verify(
    confidence: float,
    action_results: List[Dict],
    response_text: str,
    threshold: float = 0.7,
) -> bool:
    """
    Decide whether to escalate.

    Rules:
    - Do not escalate if any tool handled the request successfully.
    - Do not escalate if we produced any safe canned response (substring match).
    - Escalate if confidence is below threshold and nothing safe handled the request.
    - Default: escalate (unrecognized state).
    """
    # 1. Tool handled successfully → no escalation
    if action_results and any(r.get("status") == "ok" for r in action_results):
        return False

    # 2. If we produced a canned response (including unknown) → safe, no escalation
    if response_text:
        for canned in responses.DEFAULT_RESPONSES.values():
            if canned and canned in response_text:
                return False

    # 3. Otherwise, if low confidence → escalate
    if confidence < threshold:
        return True

    # 4. Default: escalate (unrecognized state)
    return True
