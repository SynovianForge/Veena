import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ GEMINI_API_KEY missing in .env file")
    return api_key

def configure_model(model_name="gemini-2.5-flash-lite"):
    """Return a configured Gemini model client."""
    genai.configure(api_key=get_api_key())
    return genai.GenerativeModel(model_name)

def create_bots():
    """Initialize all bot instances."""
    genai.configure(api_key=get_api_key())
    main_bot = genai.GenerativeModel("gemini-2.5-flash-lite")
    summary_bot = genai.GenerativeModel("gemini-2.5-flash-lite")  # can be changed later
    return main_bot, summary_bot
