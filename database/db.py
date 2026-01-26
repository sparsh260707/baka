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
couples_col = db["couples"]

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
    user_data.setdefault("groups", [])
    user_data.setdefault("name", getattr(user, "first_name", f"User_{uid}"))
    user_data.setdefault("bal", 0)
    user_data.setdefault("dead_until", 0)
    user_data.setdefault("protect_until", 0)
    user_data.setdefault("kills", 0)
    user_data.setdefault("rob", 0)

    # ===== Group tracking =====
    if chat_id is not None and chat_id not in user_data["groups"]:
        users_col.update_one(
            {"id": uid},
            {"$addToSet": {"groups": chat_id}}
        )
        user_data["groups"].append(chat_id)

    return user_data

def get_group_members(chat_id):
    """
    Returns all users who are members of this group.
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

# ===== ECONOMY SYSTEM =====
def is_economy_on(chat_id):
    """
    Default = True
    """
    res = settings_col.find_one({"chat_id": chat_id})
    return res.get("economy_status", True) if res else True

def set_economy_status(chat_id, status: bool):
    settings_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"economy_status": bool(status)}},
        upsert=True
    )

# ===== COUPLE SYSTEM =====
def get_couple(chat_id, date):
    """
    Fetch couple of the day from MongoDB.
    """
    return couples_col.find_one({"chat_id": chat_id, "date": date})

def save_couple(chat_id, date, couple_data):
    """
    Save today's couple to MongoDB.
    """
    couples_col.update_one(
        {"chat_id": chat_id, "date": date},
        {
            "$set": {
                "chat_id": chat_id,
                "date": date,
                "c1_id": couple_data["c1_id"],
                "c2_id": couple_data["c2_id"],
                "image": couple_data["image"],
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )

# ===== INDEXES =====
try:
    users_col.create_index("id", unique=True)
    settings_col.create_index("chat_id", unique=True)
    groups_claim_col.create_index("chat_id", unique=True)
    couples_col.create_index([("chat_id", 1), ("date", 1)], unique=True)
except Exception:
    pass
