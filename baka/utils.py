# baka/utils.py

from datetime import datetime
from pathlib import Path
import os

from database import db  # import db.py from database folder


# =========================
# CONFIG / GLOBALS
# =========================

# 🔴 Apna Telegram ID yaha daalo
SUDO_USERS = [
    8432723762,  # <-- apna real telegram id yaha daalo
]

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
TEMP_DIR = BASE_DIR / "temp"

ASSETS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)


# =========================
# USER HELPER
# =========================

def get_mention(user: dict) -> str:
    """
    Returns an HTML mention of a user.
    Works with DB user dict:
    {
        "id": user_id,
        "name": "User",
        ...
    }
    """
    user_id = user.get("id")
    name = user.get("name", "User")
    return f'<a href="tg://user?id={user_id}">{name}</a>'


# =========================
# COUPLE HELPER (MongoDB)
# =========================

def get_couple(chat_id, date):
    """
    Returns today's couple for a chat from MongoDB.
    """
    couple = db.get_couple(chat_id, date)
    if couple:
        return {
            "c1_id": couple.get("c1_id"),
            "c2_id": couple.get("c2_id"),
            "image": couple.get("image")
        }
    return None


def save_couple(chat_id, date, couple_data, img_path):
    """
    Saves today's couple to MongoDB.
    couple_data = {"c1_id": ..., "c2_id": ...}
    img_path = local path of the generated image
    """
    db.save_couple(chat_id, date, {
        "c1_id": couple_data["c1_id"],
        "c2_id": couple_data["c2_id"],
        "image": img_path
    })


def get_image(chat_id, date):
    """
    Returns saved couple image path for a chat.
    """
    couple = db.get_couple(chat_id, date)
    if couple:
        return couple.get("image")
    return None


# =========================
# DATE HELPER
# =========================

def today_str():
    return datetime.now().strftime("%Y-%m-%d")
