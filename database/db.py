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

def get_user(data, user):
    uid = str(user.id)
    if uid not in data:
        data[uid] = {
            "name": user.first_name,
            "bal": 50,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0
        }
    return data[uid]
