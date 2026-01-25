import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]
users_col = db["users"]

def get_user(user, chat_id=None):
    if not user or not hasattr(user, 'id'):
        return None

    uid = user.id
    user_data = users_col.find_one({"id": uid})

    if not user_data:
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
    return [u for u in cursor if u is not None]
