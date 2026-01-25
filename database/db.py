import json

DB_FILE = "database/users.json"

def load():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(data, user, chat_id=None):
    uid = str(user.id)

    if uid not in data:
        data[uid] = {
            "name": user.first_name,
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0,
            "groups": []
        }

    # Save group info
    if chat_id is not None:
        if chat_id not in data[uid]["groups"]:
            data[uid]["groups"].append(chat_id)

    return data[uid]
