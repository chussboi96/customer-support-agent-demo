# app.py
from __future__ import annotations

import streamlit as st
from core.workflow import support_agent_workflow
from services.db_logger import init_db
from config import settings
from core.nodes import logger as logger_node


# ---------------- Page Setup ----------------
st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="🤖",
    layout="wide",
)

# Init DB
init_db()

# ---------------- Session State ----------------
if "history" not in st.session_state:
    st.session_state["history"] = []  # [(role, payload)]
if "onboarded" not in st.session_state:
    st.session_state["onboarded"] = False
if "prefill" not in st.session_state:
    st.session_state["prefill"] = ""
if "feedback" not in st.session_state:
    st.session_state["feedback"] = {}  # log_id → feedback


# ---------------- Global CSS ----------------
st.markdown(
    """
    <style>
    .stChatMessage p, .stMarkdown p, .stMarkdown li { font-size: 1.05rem !important; }
    .stMetric label, .stMetricValue { font-size: 1.05rem !important; }
    div[data-baseweb="textarea"] > textarea {
        min-height: 120px !important;
        font-size: 1.1rem !important;
        line-height: 1.5 !important;
        resize: vertical !important;
    }
    h1, h2, h3 { font-size: 1.30rem !important; }

    @keyframes fadeInUp { from {opacity:0; transform: translateY(6px);} to {opacity:1; transform: translateY(0);} }
    @keyframes pulseSoft { 0% { box-shadow: 0 0 0 0 rgba(30,144,255,0.35);} 70% { box-shadow: 0 0 0 8px rgba(30,144,255,0);} 100% { box-shadow: 0 0 0 0 rgba(30,144,255,0);} }
    @keyframes blinkDots { 0% {opacity: .25;} 50% {opacity: 1;} 100% {opacity: .25;} }

    .stChatMessage { animation: fadeInUp 260ms ease-out; }

    .typing-indicator { display:inline-flex; gap:6px; align-items:center; }
    .typing-dot { width:8px; height:8px; border-radius:50%; background: currentColor; animation: blinkDots 1s infinite; }
    .typing-dot:nth-child(2){ animation-delay: .2s; }
    .typing-dot:nth-child(3){ animation-delay: .4s; }

    .badge { display:inline-block; padding: 4px 10px; border-radius: 999px; font-size: .85rem; font-weight: 600; margin-right:8px; }
    .badge-pill { background: #e5e7eb; border:1px solid #d1d5db; color:#111827; }
    .badge-pulse { animation: pulseSoft 2s infinite; }

    .streamlit-expanderHeader { font-size: 1.05rem !important; }

    .welcome-card { border:1px solid #d1d5db; border-radius:18px; padding:22px; background: var(--background-color); box-shadow: 0 6px 18px rgba(0,0,0,.04); animation: fadeInUp 300ms ease-out; color: inherit; }
    .quick-chip { display:inline-block; padding:8px 12px; border:1px solid #d1d5db; border-radius:999px; margin:4px; cursor:pointer; user-select:none; }
    .quick-chip:hover { background:#f3f4f6; }

    .stChatMessage, .stMarkdown p, .stMarkdown li {
        color: inherit !important;
        background-color: var(--background-color) !important;
        border-radius: 12px;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- Sidebar Controls ----------------
st.sidebar.header("⚙️ Settings")
ollama_model = st.sidebar.text_input("Ollama model", value=settings.OLLAMA_MODEL)
confidence_threshold = st.sidebar.slider(
    "Confidence Threshold",
    0.0,
    1.0,
    float(settings.CONFIDENCE_THRESHOLD),
    0.05,
)
use_mock = st.sidebar.checkbox("Use Mock APIs", value=True)
show_debug = st.sidebar.checkbox("Show Debug Info", value=True)


# ---------------- Title ----------------
st.title("🤖 Customer Support Chat Agent")


# ---------------- Onboarding ----------------
if not st.session_state["onboarded"] and len(st.session_state["history"]) == 0:
    st.caption(
        "Your all-in-one, privacy-friendly assistant for orders, refunds, and FAQs — powered by your local Ollama model."
    )

    st.markdown(
        """
        <div class="welcome-card">
            <h3>👋 Welcome!</h3>
            <p>Ask about order status, refunds, subscriptions, or general FAQs. The agent can detect multiple intents, gauge sentiment & urgency, call tools, and escalate if needed.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Try one of these to get started")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Where is my order ORD1234?", use_container_width=True):
            st.session_state["prefill"] = "Where is my order ORD1234?"
            st.session_state["onboarded"] = True
            st.rerun()
    with c2:
        if st.button("I want to cancel and refund my last order", use_container_width=True):
            st.session_state["prefill"] = "I want to cancel and refund my last order"
            st.session_state["onboarded"] = True
            st.rerun()
    with c3:
        if st.button("Change my subscription to annual", use_container_width=True):
            st.session_state["prefill"] = "Change my subscription to annual"
            st.session_state["onboarded"] = True
            st.rerun()

if st.session_state.get("prefill"):
    st.session_state["onboarded"] = True


# ---------------- Chat Input ----------------
prefill_value = st.session_state.get("prefill", "")
user_input = st.chat_input("💬 Type your message here…", key="chat_input")
if prefill_value and not user_input:
    user_input = prefill_value
    st.session_state["prefill"] = ""


# ---------------- Run Workflow ----------------
if user_input:
    st.session_state["history"].append(("user", user_input))

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            "<div class='typing-indicator' aria-label='AI is typing'>"
            "<span class='typing-dot'></span><span class='typing-dot'></span><span class='typing-dot'></span>"
            "</div>",
            unsafe_allow_html=True,
        )
        state = support_agent_workflow(
            user_input,
            model=ollama_model,
            threshold=confidence_threshold,
            use_mock=use_mock,
        )
        typing_placeholder.empty()

    # Save to DB → attach log_id
    log_id = logger_node.log_interaction(state)
    state["log_id"] = log_id

    st.session_state["history"].append(("assistant", state))


# ---------------- Conversation Rendering ----------------
for role, item in st.session_state["history"]:
    if role == "user":
        st.chat_message("user").write(item)
    else:
        agent_block = st.chat_message("assistant")
        response_text = item.get("response_text", "[No response generated]")
        agent_block.write(response_text)

        # Badges
        sentiment = item.get("sentiment", "neutral")
        urgency = item.get("urgency", "low")
        is_escalated = bool(item.get("escalation_flag"))
        badges_html = f"""
        <div style='margin:6px 0 12px 0;'>
            <span class='badge badge-pill badge-pulse' title='Sentiment'>{sentiment.capitalize()} 😊</span>
            <span class='badge badge-pill' title='Urgency'>Urgency: {urgency.capitalize()} ⏱️</span>
            <span class='badge badge-pill' title='Escalation'>{'Escalation: Yes' if is_escalated else 'Escalation: No'} 🧑‍💼</span>
        </div>
        """
        agent_block.markdown(badges_html, unsafe_allow_html=True)

        # Feedback buttons
        log_id = item.get("log_id")
        if log_id:
            fb_col1, fb_col2 = agent_block.columns(2)
            with fb_col1:
                if st.button("👍", key=f"up_{log_id}"):
                    logger_node.log_feedback(log_id, "up")
                    st.session_state["feedback"][log_id] = "up"
                    st.rerun()
            with fb_col2:
                if st.button("👎", key=f"down_{log_id}"):
                    logger_node.log_feedback(log_id, "down")
                    st.session_state["feedback"][log_id] = "down"
                    st.rerun()

            if log_id in st.session_state["feedback"]:
                agent_block.caption(f"Feedback: {st.session_state['feedback'][log_id]}")

        # Action results
        with agent_block.expander("🛠️ Action Results"):
            st.json(item.get("action_results", []))

        # Debug info
        if show_debug:
            with agent_block.expander("🧾 Debug Info"):
                st.write("Confidence:", item.get("confidence_score"))
                st.write("Intents:", item.get("intents"))
                st.write("Entities:", item.get("metadata", {}).get("entities"))
                st.write("Escalation payload:", item.get("metadata", {}).get("escalation_payload"))
