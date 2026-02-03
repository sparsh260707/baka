# config.py
import os
from dotenv import load_dotenv

# ========================
# Load .env
# ========================
load_dotenv()

# ========================
# Required Vars
# ========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")
LOG_CHAT_ID = os.getenv("LOG_CHAT_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")  # without @

# ========================
# Validation
# ========================
if not BOT_TOKEN:
    raise Exception("❌ BOT_TOKEN not found in .env file")

if not MONGO_URL:
    raise Exception("❌ MONGO_URL not found in .env file")

if not LOG_CHAT_ID:
    raise Exception("❌ LOG_CHAT_ID not found in .env file")

if not BOT_USERNAME:
    raise Exception("❌ BOT_USERNAME not found in .env file (without @)")

try:
    LOG_CHAT_ID = int(LOG_CHAT_ID)
except ValueError:
    raise Exception("❌ LOG_CHAT_ID must be a number (e.g. -100xxxxxxxxxx)")

# ========================
# Optional / Owner
# ========================
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
