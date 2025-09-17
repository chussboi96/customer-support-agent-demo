from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Ollama local server
OLLAMA_URL = "http://localhost:11434"

# Ollama model to use
OLLAMA_MODEL = "gemma3:1b"

# Confidence threshold (0-1)
CONFIDENCE_THRESHOLD = 0.6

# Database path for logs
DB_PATH = BASE_DIR / "data" / "agent_logs.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)