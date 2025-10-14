import os
from config_flags import ENABLE_MEMORY, ENABLE_JSON_LOG, ENABLE_SUMMARIES
from utils.memory import add_message
from utils.logger import append_txt

class Controller:
    def __init__(self, main_bot, summary_bot, memory=None, web=None):
        self.main_bot = main_bot
        self.summary_bot = summary_bot
        self.memory = memory or {}
        self.web = web  # placeholder for a real web search adapter

    def execute_plan(self, plan, history, user_input: str = ""):
        """Execute a planned sequence of actions. Returns list of dicts with results."""
        results = []
        steps = (plan or {}).get("steps", [])

        # Safety: ensure last step is a communication step
        if steps and steps[-1].get("action") not in {"send_to_main_chat", "clarify_context"}:
            steps.append({
                "action": "send_to_main_chat",
                "reason": "Deliver final result to user.",
                "confidence": 0.5,
                "details": {"topic": "general response", "style": "concise"}
            })

        for step in steps:
            action = step.get("action", "")
            details = step.get("details", {}) or {}
            reason = step.get("reason", "")

            if action == "send_to_main_chat":
                output = self._send_to_main_chat(details, history, user_input)
            elif action == "summarize_session":
                output = self._summarize_session(details, history)
            elif action == "query_memory":
                output = self._query_memory(details)
            elif action == "update_memory":
                output = self._update_memory(details)
            elif action == "web_search":
                output = self._web_search(details)
            elif action == "clarify_context":
                qs = details.get("questions", ["Could you clarify?"])
                output = "I need clarification: " + " ".join(qs)
            elif action == "idle":
                output = details.get("note", "No action required.")
            else:
                output = f"[Unknown action: {action}]"

            results.append({"action": action, "result": output, "reason": reason})

        return results

    # ===== Action Handlers =====

    def _send_to_main_chat(self, details, history, user_input: str):
        topic = details.get("topic", "general conversation")
        style = details.get("style", "concise")
        memory_context = getattr(self, "last_memory", "") if ENABLE_MEMORY else ""
        memory_text = f"\n\nRelevant past memory:\n{memory_context}" if memory_context else ""
        search_context = getattr(self, "last_search_results", "")
        search_text = f"\n\nWeb search context:\n{search_context}" if search_context else ""

        prompt = f"""
    You are Synovian, the main conversational agent.
    • Keep replies short (1–3 sentences) and natural.
    • If memory context is provided, use it to answer truthfully.
    • Use web search context if present.

    User's message:
    \"\"\"{user_input}\"\"\"

    {memory_text}
    {search_text}

    Topic hint: {topic}
    """.strip()

        try:
            response = self.main_bot.generate_content(prompt)
            text = (response.text or "").strip() or "[No response generated]"
        except Exception as e:
            text = f"[Main bot error: {e}]"

        self.last_search_results = ""  # clear after use
        add_message(history, "model", text)
        append_txt(history)
        return text
    

    def _summarize_session(self, details, history):
        scope = details.get("scope", "entire_session")
        fmt = details.get("format", "bullet")
        if not history:
            return "[Nothing to summarize]"
        prompt = f"Summarize this {scope} in {fmt} format:\n{history}"
        try:
            resp = self.summary_bot.generate_content(prompt)
            return (resp.text or "").strip() or "[Empty summary]"
        except Exception as e:
            return f"[Summary error: {e}]"

    def _query_memory(self, details):
        if not ENABLE_MEMORY:
            self.last_memory = ""  # ensure empty
            return "[Memory disabled]"
        from utils.memory import retrieve_from_memory
        section = details.get("section", "general")
        query = details.get("query", "")
        results = retrieve_from_memory(query, section)
        self.last_memory = "\n\n".join(r["match"] for r in results)
        return self.last_memory or "[No relevant memory found]"


    def _update_memory(self, details):
        if not ENABLE_MEMORY:
            return "[Memory disabled]"
        section = details.get("section", "general")
        data = details.get("data", "")
        self.memory[section] = data
        return f"[Updated memory section '{section}' with '{data}']"

    def _web_search(self, details):
        """Web search temporarily disabled."""
        query = details.get("query", "")
        goal = details.get("goal", "")
        return f"[Web search skipped — feature disabled. Query would have been: '{query}' ({goal})]"



    # --------------------------------------------------------
    # End-of-session summarization and JSON logging
    # --------------------------------------------------------
    def finalize_session(self, history):
        # If both summaries and json disabled, do nothing
        if not ENABLE_SUMMARIES and not ENABLE_JSON_LOG:
            print("💾 Memory features disabled — nothing to save beyond chat_log.txt.")
            return

        from datetime import datetime
        from utils.logger import append_json_with_summary

        if not history:
            print("💾 Nothing to save — empty session.")
            return

        session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build summary only if summaries enabled
        summary_text = ""
        if ENABLE_SUMMARIES:
            summary_prompt = f"""
    Summarize this chat session in structured bullet points.

    🕒 Session Timestamp: {session_time}

    Conversation:
    {history}
    """
            try:
                response = self.summary_bot.generate_content(summary_prompt)
                summary_text = (response.text or "").strip() or "[No summary generated.]"
            except Exception as e:
                summary_text = f"[Summary generation error: {e}]"

            # Append to text summary file
            os.makedirs("chat_logs", exist_ok=True)
            with open(os.path.join("chat_logs", "session_summaries.txt"), "a", encoding="utf-8") as f:
                f.write(f"\n=== Summary ({session_time}) ===\n")
                f.write(summary_text + "\n" + "-" * 70 + "\n")

        # Append JSON only if json logging enabled
        if ENABLE_JSON_LOG:
            append_json_with_summary(history, summary_text)

        print("💾 Session persisted:",
            "TXT", 
            "+ SUMMARIES" if ENABLE_SUMMARIES else "",
            "+ JSON" if ENABLE_JSON_LOG else "")
