from datetime import datetime, timedelta
from database.db import db

boss_col = db.boss_events

def register_user(user_id, username, group_id):
    today = datetime.utcnow().date().isoformat()

    event = boss_col.find_one({"group_id": group_id, "date": today})
    if not event:
        boss_col.insert_one({
            "group_id": group_id,
            "date": today,
            "status": "waiting",
            "participants": {},
            "boss_hp": 100000
        })

    event = boss_col.find_one({"group_id": group_id, "date": today})

    if event["status"] != "waiting":
        return False

    event["participants"][str(user_id)] = {
        "username": username,
        "damage": 0,
        "attacks": 0
    }

    boss_col.update_one(
        {"_id": event["_id"]},
        {"$set": {"participants": event["participants"]}}
    )
    return True
