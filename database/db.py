import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017"

client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]
users_col = db["users"]

# --- COMPATIBILITY FUNCTIONS (Economy.py ke liye) ---
def load():
    """Purane JSON logic ke liye dummy function taaki bot crash na ho."""
    return {}

def save(data):
    """Purane JSON logic ke liye dummy function."""
    pass
# --------------------------------------------------

def get_user(user, chat_id=None):
    """User ko MongoDB mein register/update karta hai."""
    if not user or not hasattr(user, 'id'):
        return None

    uid = user.id
    user_data = users_col.find_one({"id": uid})

    if not user_data:
        # Naya user document
        user_data = {
            "id": uid,
            "name": getattr(user, 'first_name', "Unknown"),
            "groups": [],
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0
        }
        users_col.insert_one(user_data)
    
    if chat_id is not None:
        # User ko group list mein add karna
        users_col.update_one(
            {"id": uid},
            {"$addToSet": {"groups": chat_id}}
        )
        user_data = users_col.find_one({"id": uid})

    return user_data

def get_group_members(chat_id):
    """NoneType error safety ke saath members fetch karta hai."""
    query = {"groups": chat_id}
    cursor = users_col.find(query)
    # Filter None values to prevent crashes
    return [u for u in cursor if u is not None]
