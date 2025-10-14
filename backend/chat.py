# chat.py
import sys
from datetime import datetime
from utils.memory import add_message, trim_history
from utils.logger import append_txt, append_json_with_summary

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def chat_loop(main_bot, summary_bot):
    """Interactive chat loop with structured summarization and JSON storage."""
    history = []
    print("🤖 Gemini Chatbot (Streaming + Summary + JSON Memory)")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("\n💾 Saving chat logs and generating structured summary...\n")
            append_txt(history)

            # === Generate structured summary ===
            session_time = timestamp()
            structured_prompt = f"""
You are the Summary Bot for a developer's AI chat system.

Summarize the following conversation in detailed, structured bullet points.
Each category should have at least a few items when possible.

Include the current timestamp: {session_time}

Format exactly as follows:

🕒 Session Timestamp: {session_time}

🧩 Session Context:
• Describe the purpose and setup of this session.
• Mention what tools, bots, or files were involved.

✅ Actions Taken:
• List concrete actions or changes made.

📚 Concepts or Skills Learned:
• Highlight new concepts, frameworks, or debugging insights.

⚙️ Changes / Improvements Made:
• Summarize all code refactors, optimizations, or architecture changes.

💡 Key Insights / Lessons:
• Extract major reasoning or conceptual takeaways.

🧠 Unresolved Questions / TODOs:
• Note pending questions or next steps.

🔁 Follow-Up Ideas / Next Steps:
• Suggest future directions or experiments.

⚠️ Issues / Bugs / Risks Observed:
• Mention errors, runtime issues, or fragile parts.

🧭 Overall Summary:
• End with a concise, reflective summary (2–3 lines).

Conversation to analyze:
{history}
            """

            try:
                summary_response = summary_bot.generate_content(structured_prompt)
                summary_text = summary_response.text.strip()

                print("🧭 Session Summary:\n")
                print(summary_text)
                print("\n")

                # Append to both text and JSON logs
                append_json_with_summary(history, summary_text)

                # Also store separately in summaries.txt
                with open("chat_logs/session_summaries.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n=== Summary ({session_time}) ===\n")
                    f.write(summary_text + "\n" + "-" * 70 + "\n")

            except Exception as e:
                print(f"⚠️ Could not generate summary: {e}\n")
                append_json_with_summary(history, "[Summary generation failed]")

            print("✅ Logs updated in chat_logs/")
            print("👋 Goodbye!")
            break

        if not user_input:
            continue

        history = add_message(history, "user", user_input)
        print("Gemini: ", end="", flush=True)

        try:
            response = main_bot.generate_content(history, stream=True)
            full_text = ""
            for chunk in response:
                if chunk.text:
                    print(chunk.text, end="", flush=True)
                    full_text += chunk.text
            print("\n")

            history = add_message(history, "model", full_text)
            history = trim_history(history)

        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")

    sys.exit(0)
