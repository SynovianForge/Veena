import json
import re
import google.generativeai as genai

# ============================================================
#  SYSTEM PROMPT — STRICT JSON MODE + END-WITH-COMMUNICATION
# ============================================================
SYSTEM_PROMPT = """
You are Orchestrator — a control-plane agent that decides how a multi-bot AI system
should handle user requests. You never perform the tasks yourself; you only create
a structured plan of actions in valid JSON.

Your objectives:
1. Parse the user's input.
2. Break it into one or more ordered steps.
3. Each step must include:
   • action — operation type.
   • reason — one-sentence justification.
   • confidence — float between 0 and 1.
   • details — fine-grained parameters for that action.

Recognized actions and expected detail keys:

- send_to_main_chat → details: { "topic": "<topic of conversation>", "style": "<concise|friendly|explanatory|creative>" }
- query_memory → details: { "section": "<memory category>", "query": "<specific info to recall>" }
- update_memory → details: { "section": "<where to store>", "data": "<what to store>" }
- summarize_session → details: { "scope": "<entire_session|last_task|errors_only>", "format": "<text|bullet|json>" }
- web_search → details: { "query": "<search string>", "goal": "<why this search matters>" }
- analyze_data → details: { "file_type": "<csv|txt|image>", "analysis_goal": "<goal>" }
- generate_plan → details: { "objective": "<goal to plan for>", "steps_required": "<approx number of steps>" }
- clarify_context → details: { "questions": ["list of clarifying questions"] }
- run_code → details: { "language": "<python|javascript|other>", "task": "<what to compute>" }
- idle → details: { "note": "small talk or no action needed" }

Output Format Rules:
- Respond ONLY with a valid JSON object.
- No code fences, no prose, no explanations.
- The first character of your response must be '{' and the last must be '}'.
- Always end the plan with a communication step ("send_to_main_chat" or "clarify_context").
- If uncertain, still return a valid JSON object:
  {"steps":[{"action":"clarify_context","reason":"unclear","confidence":0.0,"details":{"questions":["Could you rephrase that?"]}}]}
"""

# ============================================================
#  ORCHESTRATOR CLASS
# ============================================================
class Orchestrator:
    def __init__(self, model):
        # configure model (force low temperature for deterministic JSON)
        self.model = genai.GenerativeModel(
            model.model_name,
            generation_config={"temperature": 0}
        )

    def plan(self, user_input: str):
        """Generate and safely parse a JSON action plan from user input."""
        prompt = SYSTEM_PROMPT + f"\nUser: {user_input}"

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text.strip()
        except Exception as e:
            print(f"⚠️ Model error: {e}")
            return self._fallback_plan("Model generation error")

        # --- Debug print (optional) ---
        # print("🧩 Raw orchestrator output:\n", raw_text)

        cleaned = self._extract_json(raw_text)

        try:
            plan = json.loads(cleaned)
        except Exception as e:
            print(f"[Parser warning: {e}] Raw output:\n{raw_text}\n")
            plan = self._fallback_plan("Failed to parse orchestrator output")

        return plan

    # --------------------------------------------------------
    # Internal helper: regex-based JSON extraction
    # --------------------------------------------------------
    def _extract_json(self, text: str) -> str:
        """Clean markdown/code fences and extract JSON substring."""
        # remove code fences like ```json or ```
        cleaned = re.sub(r"```(?:json)?", "", text).strip()
        # extract first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return match.group(0).strip()
        return cleaned

    # --------------------------------------------------------
    # Fallback plan when JSON parsing fails
    # --------------------------------------------------------
    def _fallback_plan(self, reason: str):
        return {
            "steps": [
                {
                    "action": "clarify_context",
                    "reason": reason,
                    "confidence": 0.0,
                    "details": {
                        "questions": ["Could you clarify what you meant?"]
                    },
                }
            ]
        }
