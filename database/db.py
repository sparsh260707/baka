import json
from pathlib import Path

# DB file path (baka/database/users.json)
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

    # Chat ID ko register karna (taaki couple command me kaam aaye)
    if chat_id is not None:
        if chat_id not in data[uid]["groups"]:
            data[uid]["groups"].append(chat_id)

    save(data)
    return data[uid]

def get_group_members(chat_id):
    """Uss group ke saare members (Offline/Online) return karta hai."""
    data = load()
    members = []
    
    # Target chat_id ko search karna
    for uid, user_data in data.items():
        user_groups = user_data.get("groups", [])
        
        # Check both int and string format for safety
        if chat_id in user_groups or str(chat_id) in user_groups:
            members.append(user_data)
            
    return members
