# services/mock_api.py
from typing import Dict, Any, Optional
import random
import datetime
import re


def _extract_order_id(text: str) -> Optional[str]:
    """
    Extract an order ID from text if it matches pattern ORD####.
    """
    match = re.search(r"\bORD\d{3,}\b", text.upper())
    return match.group(0) if match else None


def check_order_status_tool(normalized_input: str) -> Dict[str, Any]:
    """
    Simulate checking order status. If an order ID is found in the input,
    use it; otherwise, generate a random one.
    """
    order_id = _extract_order_id(normalized_input) or f"ORD{random.randint(1000, 9999)}"
    shipped = random.choice([True, False])

    return {
        "tool": "check_order_status",
        "status": "ok",
        "order_id": order_id,
        "shipped": shipped,
        "estimated_delivery": (
            datetime.date.today() + datetime.timedelta(days=random.randint(2, 7))
        ).isoformat(),
        "message": f"Order {order_id} is {'shipped' if shipped else 'processing'}."
    }


def initiate_refund_tool(normalized_input: str) -> Dict[str, Any]:
    """
    Simulate initiating a refund. If an order ID is found in input,
    link refund to that order; otherwise, generate only refund id.
    """
    order_id = _extract_order_id(normalized_input)
    refund_id = f"RFD{random.randint(10000, 99999)}"

    return {
        "tool": "initiate_refund",
        "status": "ok",
        "refund_id": refund_id,
        "order_id": order_id,
        "message": (
            f"Refund {refund_id} initiated for {order_id}. "
            "Funds should reflect in 5–7 business days."
            if order_id else
            f"Refund {refund_id} initiated. Funds should reflect in 5–7 business days."
        )
    }


def open_ticket_tool(normalized_input: str) -> Dict[str, Any]:
    """
    Simulate opening a support ticket.
    """
    ticket_id = f"TKT{random.randint(100000, 999999)}"

    return {
        "tool": "open_ticket",
        "status": "ok",
        "ticket_id": ticket_id,
        "message": f"Ticket {ticket_id} created. Support will contact you within 24 hours."
    }
