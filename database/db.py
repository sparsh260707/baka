import json
from pathlib import Path

DB_FILE = Path("database/users.json")

def load():
    try:
        if not DB_FILE.exists(): return {}
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    try:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def get_user(user, chat_id=None):
    # Safety Check: Agar user object null hai toh wahin ruk jao
    if not user or not hasattr(user, 'id'):
        return None

    data = load()
    uid = str(user.id)

    if uid not in data:
        data[uid] = {
            "id": user.id,
            "name": getattr(user, 'first_name', "Unknown"),
            "groups": [],
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0
        }
    
    # Purane users ke liye check
    if "groups" not in data[uid]:
        data[uid]["groups"] = []

    if chat_id is not None:
        if chat_id not in data[uid]["groups"]:
            data[uid]["groups"].append(chat_id)

    save(data)
    return data[uid]

def get_group_members(chat_id):
    data = load()
    members = []
    for u in data.values():
        # 'id' aur 'groups' check karein bina crash hue
        if not u.get("id"): continue
        user_groups = u.get("groups", [])
        if chat_id in user_groups or str(chat_id) in user_groups:
            members.append(u)
    return members
