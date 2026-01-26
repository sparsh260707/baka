# baka/utils.py
from datetime import datetime
from pathlib import Path
import os

from database import db  # import db.py from database folder

# =========================
# USER HELPER
# =========================
def get_mention(user):
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
