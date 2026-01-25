import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017"

client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]

# Collections setup
users_col = db["users"]
groups_claim_col = db["groups_claim"]
settings_col = db["settings"] # Naya collection settings ke liye

# --- COMPATIBILITY FUNCTIONS (Economy/Old commands ke liye) ---
def load():
    return {}

def save(data):
    pass
# -----------------------------------------------------------

def get_user(user, chat_id=None):
    """Hamesha ek dictionary return karega taaki 'NoneType' error na aaye."""
    if not user or not hasattr(user, 'id'):
        return {"id": 0, "groups": [], "bal": 0, "name": "Unknown"}

    uid = user.id
    user_data = users_col.find_one({"id": uid})

    if not user_data:
        # Naya user document banayein
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
        # Update MongoDB and local object
        if chat_id not in user_data["groups"]:
            users_col.update_one(
                {"id": uid},
                {"$addToSet": {"groups": chat_id}}
            )
            user_data["groups"].append(chat_id)

    return user_data

def get_group_members(chat_id):
    """Group members fetch karein safety ke saath."""
    query = {"groups": chat_id}
    cursor = users_col.find(query)
    return [u for u in cursor if u is not None]

# --- CLAIM LOGIC FUNCTIONS ---

def is_group_claimed(chat_id):
    """Check karta hai ki group ne reward claim kiya hai ya nahi."""
    data = groups_claim_col.find_one({"chat_id": chat_id})
    return data is not None and data.get("claimed", False)

def mark_group_claimed(chat_id, user_id):
    """Group ko permanent claimed mark karta hai."""
    groups_claim_col.insert_one({
        "chat_id": chat_id,
        "claimed": True,
        "claimed_by": user_id,
        "at": datetime.now()
    })

# --- ECONOMY CONTROL FUNCTIONS (Open/Close) ---

def is_economy_on(chat_id):
    """Check karta hai ki iss group ki economy ON hai ya OFF."""
    res = settings_col.find_one({"chat_id": chat_id})
    return res.get("economy_status", True) if res else True

def set_economy_status(chat_id, status):
    """Economy status (True/False) ko update karta hai."""
    settings_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"economy_status": status}},
        upsert=True
    )
