import json
from pathlib import Path

DB_FILE = Path("database/users.json")

def load():
    """Load users data from JSON."""
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save(data):
    """Save users data to JSON."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(user, chat_id=None):
    """Get or create a user entry."""
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

    if chat_id is not None and chat_id not in data[uid]["groups"]:
        data[uid]["groups"].append(chat_id)

    save(data)
    return data[uid]

def get_group_members(chat_id):
    """Return all users in a specific group."""
    data = load()
    return [u for u in data.values() if chat_id in u.get("groups", [])]
