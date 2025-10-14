# utils/memory.py
import json
import os
from datetime import datetime

LOG_DIR = "chat_logs"
JSON_LOG_PATH = os.path.join(LOG_DIR, "chat_log.json")
SUMMARIES_PATH = os.path.join(LOG_DIR, "session_summaries.txt")

def init_history():
    """Initialize a new conversation history."""
    return []

def add_message(history, role, text):
    """Append a message to the conversation history."""
    history.append({"role": role, "parts": [text]})
    return history

def trim_history(history, max_turns=12):
    """Keep history length under control."""
    if len(history) > max_turns:
        history = history[-max_turns:]
    return history

# ===========================================================
# Memory Retrieval Layer
# ===========================================================

def load_memory():
    """Load JSON chat memory. Returns list of sessions."""
    if not os.path.exists(JSON_LOG_PATH):
        return []
    with open(JSON_LOG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def retrieve_from_memory(query: str, section: str = None, limit: int = 3):
    """
    Bare-bones keyword search through session_summaries.txt.
    Returns up to <limit> matching excerpts.
    """
    summaries_path = os.path.join("chat_logs", "session_summaries.txt")
    if not os.path.exists(summaries_path):
        return [{"timestamp": None, "match": "[No memory file found]"}]

    results = []
    with open(summaries_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    joined = "".join(lines)
    lower = joined.lower()
    idx = 0
    while True:
        pos = lower.find(query.lower(), idx)
        if pos == -1 or len(results) >= limit:
            break
        start = max(0, pos - 200)
        end = min(len(joined), pos + 200)
        snippet = joined[start:end].strip().replace("\n", " ")
        results.append({"timestamp": None, "match": snippet + "..."})
        idx = pos + len(query)

    if not results:
        return [{"timestamp": None, "match": "[No matching memory found]"}]

    return results

def _shorten(text, query, window=180):
    """Return a small excerpt around the query term."""
    idx = text.lower().find(query.lower())
    if idx == -1:
        return text[:window] + "..." if len(text) > window else text
    start = max(0, idx - window // 2)
    end = min(len(text), idx + window // 2)
    return text[start:end].strip() + "..."
