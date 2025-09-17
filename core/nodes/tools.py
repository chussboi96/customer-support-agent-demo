# core/nodes/tools.py
from typing import List, Dict, Any
from services.mock_api import check_order_status_tool, initiate_refund_tool, open_ticket_tool

def call_tools_for_intents(intents: List[str], normalized_input: str, entities: Dict[str, Any] | None = None, use_mock: bool = True) -> List[Dict[str, Any]]:
    """
    Call appropriate tool handlers for detected intents.
    Entities (like order_id or email) will be forwarded to tools when available.
    """
    results: List[Dict[str, Any]] = []
    for intent in intents:
        if intent == "order_status":
            # pass entities if present
            res = check_order_status_tool(normalized_input) if use_mock else {"tool": "check_order_status", "status": "unhandled", "intent": intent}
            # ensure order_id preferred from entities if detected
            if entities and entities.get("order_id") and res.get("order_id") != entities.get("order_id"):
                res["order_id"] = entities.get("order_id")
                res["message"] = f"Order {res['order_id']} status adjusted based on extracted entity."
            results.append(res)
        elif intent == "refund":
            res = initiate_refund_tool(normalized_input) if use_mock else {"tool": "initiate_refund", "status": "unhandled", "intent": intent}
            # if we detected an order_id entity, attach it
            if entities and entities.get("order_id"):
                res["order_id"] = entities.get("order_id")
            results.append(res)
        elif intent == "technical_issue":
            res = open_ticket_tool(normalized_input) if use_mock else {"tool": "open_ticket", "status": "unhandled", "intent": intent}
            results.append(res)
        else:
            results.append({"tool": "none", "status": "unhandled", "intent": intent})
    return results
