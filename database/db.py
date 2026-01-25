import json
from pathlib import Path

# DB file path
DB_FILE = Path("database/users.json")

def load():
    """JSON se users data load karta hai."""
    try:
        if not DB_FILE.exists():
            return {}
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading DB: {e}")
        return {}

def save(data):
    """Users data ko JSON mein save karta hai."""
    try:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving DB: {e}")

def get_user(user, chat_id=None):
    """User entry nikaalta hai ya nayi banata hai."""
    data = load()
    uid = str(user.id)

    # Agar user naya hai
    if uid not in data:
        data[uid] = {
            "id": user.id,
            "name": user.first_name,
            "groups": [],
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0
        }
    
    # Purane users ke liye safety: Agar groups key missing hai toh banado
    if "groups" not in data[uid]:
        data[uid]["groups"] = []

    # Chat ID ko register karna
    if chat_id is not None:
        if chat_id not in data[uid]["groups"] and str(chat_id) not in data[uid]["groups"]:
            data[uid]["groups"].append(chat_id)

    save(data)
    return data[uid]

def get_group_members(chat_id):
    """Uss group ke saare members return karta hai."""
    data = load()
    members = []
    
    for uid, user_data in data.items():
        # .get use karne se 'groups' key missing hone par crash nahi hoga
        user_groups = user_data.get("groups", [])
        
        if chat_id in user_groups or str(chat_id) in user_groups:
            members.append(user_data)
            
    return members
