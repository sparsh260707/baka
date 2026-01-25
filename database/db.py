import os
import pymongo
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# MongoDB Configuration
MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    print("⚠️ MONGO_URL not found in .env! Using local connection.")
    MONGO_URL = "mongodb://localhost:27017"

# Initialize Client
client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]
users_col = db["users"]

def get_user(user, chat_id=None):
    """User entry nikaalta hai ya MongoDB mein naya banata hai."""
    if not user or not hasattr(user, 'id'):
        return None

    uid = user.id
    
    # User ko find karein
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
    
    # Agar chat_id diya hai aur woh groups list mein nahi hai
    if chat_id is not None:
        # $addToSet duplicate se bachata hai aur array me add karta hai
        users_col.update_one(
            {"id": uid},
            {"$addToSet": {"groups": chat_id}}
        )
        # Update ke baad fresh data lein
        user_data = users_col.find_one({"id": uid})

    return user_data

def get_group_members(chat_id):
    """Uss group ke saare members (Offline/Online) return karta hai."""
    # MongoDB query: Unn users ko dhundo jinke 'groups' list mein ye chat_id hai
    query = {"groups": chat_id}
    members_cursor = users_col.find(query)
    
    return list(members_cursor)
