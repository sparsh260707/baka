# database/db.py
import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ===== MongoDB Connection =====
MONGO_URL = os.getenv("MONGO_URL") or "mongodb://localhost:27017"

client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]

# ===== Collections =====
users_col = db["users"]
groups_claim_col = db["groups_claim"]
settings_col = db["settings"]

# ===== Compatibility (old json system) =====
def load():
    return {}

def save(data):
    pass

# ===== USER SYSTEM =====
def get_user(user, chat_id=None):
    """
    Always returns a valid user dict.
    Auto-creates user if not exists.
    """
    if not user or not hasattr(user, "id"):
        return {
            "id": 0,
            "name": "Unknown",
            "groups": [],
            "bal": 0,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0,
        }

    uid = user.id
    user_data = users_col.find_one({"id": uid})

    if not user_data:
        user_data = {
            "id": uid,
            "name": getattr(user, "first_name", f"User_{uid}"),
            "groups": [],
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0,
            "created_at": datetime.utcnow(),
        }
        users_col.insert_one(user_data)

    # ===== Safety keys =====
    if "groups" not in user_data: user_data["groups"] = []
    if "name" not in user_data: user_data["name"] = getattr(user, "first_name", f"User_{uid}")
    if "bal" not in user_data: user_data["bal"] = 0
    if "dead_until" not in user_data: user_data["dead_until"] = 0
    if "protect_until" not in user_data: user_data["protect_until"] = 0
    if "kills" not in user_data: user_data["kills"] = 0
    if "rob" not in user_data: user_data["rob"] = 0

    # ===== Group tracking =====
    if chat_id is not None:
        if chat_id not in user_data["groups"]:
            users_col.update_one(
                {"id": uid},
                {"$addToSet": {"groups": chat_id}}
            )
            user_data["groups"].append(chat_id)

    return user_data

def get_group_members(chat_id):
    """
    Returns all users who are marked as members of this group.
    """
    return list(users_col.find({"groups": chat_id}))

# ===== CLAIM SYSTEM =====
def is_group_claimed(chat_id):
    data = groups_claim_col.find_one({"chat_id": chat_id})
    return bool(data and data.get("claimed", False))

def mark_group_claimed(chat_id, user_id):
    groups_claim_col.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chat_id": chat_id,
                "claimed": True,
                "claimed_by": user_id,
                "at": datetime.utcnow(),
            }
        },
        upsert=True
    )

# ===== ECONOMY ON/OFF SYSTEM =====
def is_economy_on(chat_id):
    """
    Default = ON
    """
    res = settings_col.find_one({"chat_id": chat_id})
    if not res:
        return True
    return res.get("economy_status", True)

def set_economy_status(chat_id, status: bool):
    settings_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"economy_status": bool(status)}},
        upsert=True
    )

# ===== INDEXES (optional but good for performance) =====
try:
    users_col.create_index("id", unique=True)
    settings_col.create_index("chat_id", unique=True)
    groups_claim_col.create_index("chat_id", unique=True)
except:
    pass
