import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
GROQ_KEY = os.getenv("GROQ_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")
