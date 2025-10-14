from config import create_bots
from orchestrator import Orchestrator
from controller import Controller
from utils.memory import add_message

def main():
    main_bot, summary_bot = create_bots()
    orchestrator = Orchestrator(main_bot)   # uses same model name, temp=0 inside
    controller = Controller(main_bot, summary_bot)

    print("🤖 Synovian Orchestrator Chat System")
    print("Type 'exit' to quit.\n")

    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("💾 Generating summary and saving logs...")
            controller.finalize_session(history)
            print("👋 Goodbye!")
            break
        if not user_input:
            continue

        # ✅ Append the current user message BEFORE planning
        add_message(history, "user", user_input)

        # Plan with the current input
        plan = orchestrator.plan(user_input)
        print("\n📜 Plan:", plan, "\n")

        # Execute with explicit user_input
        results = controller.execute_plan(plan, history, user_input=user_input)
        for r in results:
            print(f"⚙️ {r['action']}: {r['result']}\n")

if __name__ == "__main__":
    main()
