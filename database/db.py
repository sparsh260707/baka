import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017"

client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]
users_col = db["users"]
groups_claim_col = db["groups_claim"]

def load(): return {}
def save(data): pass

def get_user(user, chat_id=None):
    """NoneType aur Missing Key safety ke saath user fetch karta hai."""
    if not user or not hasattr(user, 'id'):
        return {"id": 0, "groups": [], "bal": 0, "name": "Unknown"}

    uid = user.id
    user_data = users_col.find_one({"id": uid})

    if not user_data:
        # Naya user document
        user_data = {
            "id": uid,
            "name": getattr(user, 'first_name', f"User_{uid}"),
            "groups": [],
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0
        }
        users_col.insert_one(user_data)
    
    # Safety: Ensure essential keys exist in returned data
    if "groups" not in user_data: user_data["groups"] = []
    if "name" not in user_data: user_data["name"] = getattr(user, 'first_name', f"User_{uid}")
    if "bal" not in user_data: user_data["bal"] = 0

    if chat_id is not None:
        if chat_id not in user_data["groups"]:
            users_col.update_one(
                {"id": uid},
                {"$addToSet": {"groups": chat_id}}
            )
            user_data["groups"].append(chat_id)

    return user_data

def get_group_members(chat_id):
    query = {"groups": chat_id}
    cursor = users_col.find(query)
    return [u for u in cursor if u is not None]

def is_group_claimed(chat_id):
    data = groups_claim_col.find_one({"chat_id": chat_id})
    return data is not None and data.get("claimed", False)

def mark_group_claimed(chat_id, user_id):
    groups_claim_col.insert_one({
        "chat_id": chat_id,
        "claimed": True,
        "claimed_by": user_id,
        "at": datetime.now()
    })
