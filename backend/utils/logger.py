# utils/logger.py
import os
import json
from datetime import datetime

LOG_DIR = "chat_logs"
os.makedirs(LOG_DIR, exist_ok=True)

TXT_LOG_PATH = os.path.join(LOG_DIR, "chat_log.txt")
JSON_LOG_PATH = os.path.join(LOG_DIR, "chat_log.json")

def timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def append_txt(history):
    """Append one session to the ongoing text log."""
    with open(TXT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write("\n\n=== Session Start " + timestamp() + " ===\n\n")
        for entry in history:
            role = entry["role"].capitalize()
            text = entry["parts"][0]
            f.write(f"{role}: {text}\n\n")
        f.write("=== Session End ===\n")

def append_json(history):
    """Append a session without summary."""
    session_data = {"timestamp": timestamp(), "messages": history}
    _append_to_json_file(session_data)

def append_json_with_summary(history, summary_text):
    """Append a session with summary included."""
    session_data = {
        "timestamp": timestamp(),
        "messages": history,
        "summary": summary_text,
    }
    _append_to_json_file(session_data)

def _append_to_json_file(session_data):
    """Private helper to append structured session data."""
    existing = []
    if os.path.exists(JSON_LOG_PATH):
        with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
    existing.append(session_data)
    with open(JSON_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
