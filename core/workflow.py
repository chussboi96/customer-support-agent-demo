# core/workflow.py

from typing import Dict, Any
from core.state import SupportAgentState
from core.nodes import (
    preprocessing,
    classifier,
    tools as tools_node,
    sentiment as sentiment_node,
    response as response_node,
    verification as verification_node,
    fallback as fallback_node,
    logger as logger_node,
    responses,  # canned replies
)
from config import settings
import yaml
from pathlib import Path

# Load intents
INTENTS_PATH = Path(__file__).resolve().parent.parent / "config" / "intents.yaml"
with open(INTENTS_PATH, "r") as f:
    intents_cfg = yaml.safe_load(f)
INTENTS_LIST = intents_cfg.get("intents", []) if isinstance(intents_cfg, dict) else []

def support_agent_workflow(
    user_input: str, model: str = None, threshold: float = None, use_mock: bool = True
) -> Dict[str, Any]:
    """
    Main orchestrator for a single user interaction.
    NOTE: This function no longer persists logs to DB — logging should be done by the caller (e.g., app.py),
    so the caller can attach the returned log id to the conversation state.
    """
    # Initialize state
    state: SupportAgentState = {
        "user_input": user_input,
        "normalized_input": "",
        "intents": [],
        "sentiment": "neutral",
        "urgency": "low",
        "action_results": [],
        "response_text": "",
        "confidence_score": 0.0,
        "escalation_flag": False,
        "log": [],
        "metadata": {},
    }

    # 1. Preprocessing
    normalized = preprocessing.normalize(user_input)
    state["normalized_input"] = normalized
    entities = preprocessing.extract_entities(normalized)
    state["metadata"]["entities"] = entities

    # 2. Multi-intent classification
    intents, confidence = classifier.classify_intent_with_ollama(
        normalized, INTENTS_LIST
    )
    # Force fallback to "unknown" if no intents returned
    if not intents:
        intents = ["unknown"]

    # Normalize again to map any variants
    intents = [responses.normalize_intent(i) for i in intents]
    state["intents"] = intents
    state["confidence_score"] = confidence

    # 3. Tool calls (pass entities)
    action_results = tools_node.call_tools_for_intents(
        intents, normalized, entities=entities, use_mock=use_mock
    )
    state["action_results"] = action_results

    # 4. Sentiment + urgency
    sentiment, urgency = sentiment_node.analyze_sentiment_with_ollama(normalized)
    state["sentiment"] = sentiment
    state["urgency"] = urgency

    # 5. Response generation
    response_text = None

    # Case A: Aggregate tool-handled messages
    success_msgs = [r.get("message") for r in action_results if r.get("status") == "ok" and r.get("message")]
    if success_msgs:
        # join them so multiple handled intents are covered
        response_text = " ".join(success_msgs)

    # Case B: Canned replies (combine multi-intents) — only if no tool message
    if not response_text and intents:
        canned = responses.combine_responses(intents)
        if canned:
            response_text = canned

    # Case C: LLM-generated fallback (if still nothing)
    if not response_text:
        response_text = response_node.ollama_generate_response(
            user_input, intents, action_results, sentiment, urgency
        )

    state["response_text"] = response_text

    # 6. Verification (now includes "unknown" as safe if canned)
    escalate = verification_node.verify(
        confidence=state["confidence_score"],
        action_results=action_results,
        response_text=response_text,
        threshold=threshold or settings.CONFIDENCE_THRESHOLD,
    )
    state["escalation_flag"] = escalate

    # 7. Fallback / Escalation
    if escalate:
        esc_payload = fallback_node.create_escalation_payload(state)
        state["metadata"]["escalation_payload"] = esc_payload
        # Short human-handoff response
        state["response_text"] = (
            "I couldn't confidently resolve this automatically. "
            "I'm escalating to a human agent who will follow up shortly."
        )

    # 8. NOTE: Logging is intentionally not performed here. Caller should call logger_node.log_interaction(state)
    return state
