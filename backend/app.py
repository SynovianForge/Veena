# backend/app.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from controller import Controller
from orchestrator import Orchestrator
from config import create_bots

main_bot, summary_bot = create_bots()
controller = Controller(main_bot, summary_bot)

app = FastAPI(title="Synovian Voice Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- FIX: define /chat BEFORE mounting static files ---
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("text", "").strip()
    print(f"\n🗣️ User said: {user_input}\n")

    orchestrator = Orchestrator(main_bot)
    plan = orchestrator.plan(user_input)
    print("📜 Plan:", plan)

    results = controller.execute_plan(plan, [], user_input)
    final_reply = results[-1]["result"] if results else "[No reply]"

    print(f"💬 Reply: {final_reply}\n")
    return {"reply": final_reply}


# --- Now mount frontend files ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "..", "web")


if not os.path.exists(WEB_DIR):
    raise RuntimeError(f"Web directory not found at: {WEB_DIR}")

app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
