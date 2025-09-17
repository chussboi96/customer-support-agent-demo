🤖 Customer Support Chat Agent
A demo customer support chat agent built with Streamlit, LangChain, and Ollama.
The agent can detect intents, analyze sentiment & urgency, call APIs (mocked), and escalate when needed. All interactions are logged locally for feedback and review.

✨ Features
- Intent Detection (refunds, order status, billing, etc.)
- Sentiment & Urgency Analysis
- Tool Integration (mock APIs for orders, refunds, tickets)
- SQLite Logging (conversations, actions, feedback)
- Escalation Handling (fallbacks when confidence is low)
- Streamlit UI with quick-start buttons, typing indicator, badges, and feedback controls


📂 Project Structure
```text
customer_support_agent/
│
├── app.py                # Main Streamlit app (UI + agent interface)
├── config/
│   ├── settings.py       # Configs (Ollama model, thresholds, DB path)
│   └── intents.yaml      # Intent definitions
├── core/
│   ├── state.py          # Defines SupportAgentState TypedDict
│   ├── workflow.py       # Workflow orchestration (nodes + transitions)
│   ├── nodes/            # Modular pipeline nodes
│   │   ├── preprocessing.py
│   │   ├── classifier.py
│   │   ├── sentiment.py
│   │   ├── tools.py
│   │   ├── response.py
│   │   ├── verification.py
│   │   ├── fallback.py
│   │   ├── logger.py
│   │   └── responses.py
│   └── utils.py          # Helper functions
├── services/
│   ├── ollama_client.py  # Wrapper for Ollama API
│   ├── mock_api.py       # Simulated order/refund/ticket APIs
│   └── db_logger.py      # SQLite logging + feedback
├── data/
│   ├── logs/             # Stored logs (SQLite/JSON)
│   └── examples.json     # Example test queries
├── requirements.txt      # Dependencies
└── README.md             # Documentation
```


🚀 Quick Start

1. Install Dependencies
- pip install -r requirements.txt

2. Install & Run Ollama
- Make sure you have Ollama installed and running locally.
Example (with llama3.1): ollama pull llama3.1 and then ollama serve
- By default, the app connects to http://localhost:11434.

3. Configure Settings
- Update config/settings.py if needed:

4. Run the Streamlit App
- streamlit run app.py


🛠 Demo Notes
- Mock APIs are used for orders, refunds, and tickets (replace with real APIs for production).
- Logs are stored in SQLite (data/logs/support_logs.db) and can be inspected.
- Feedback can be given per response (👍 / 👎).
- Debug Info can be toggled in the sidebar.

- PS: This is a demo (not production-ready).




