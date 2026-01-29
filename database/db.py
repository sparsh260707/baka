import pymongo
from datetime import datetime
from config import MONGO_URL

# =====================================================
# ================= MongoDB Connection =================
# =====================================================

client = pymongo.MongoClient(MONGO_URL)
db = client["baka_bot_db"]

# ================= Collections =================
users_col = db["users"]
groups_claim_col = db["groups_claim"]
settings_col = db["settings"]
couples_col = db["couples"]

# =====================================================
# ================= USER SYSTEM ========================
# =====================================================

def get_user(user, chat_id=None):
    if not user or not hasattr(user, "id"):
        return {
            "id": 0,
            "name": "Unknown",
            "groups": [],
            "bal": 0,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0,
        }

    uid = int(user.id)
    user_data = users_col.find_one({"id": uid})

    if not user_data:
        user_data = {
            "id": uid,
            "name": getattr(user, "first_name", f"User_{uid}"),
            "groups": [],
            "bal": 200,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0,
            "kills": 0,
            "rob": 0,
            "created_at": datetime.utcnow(),
        }
        users_col.insert_one(user_data)

    user_data.setdefault("groups", [])
    user_data.setdefault("bal", 0)
    user_data.setdefault("dead_until", 0)
    user_data.setdefault("protect_until", 0)
    user_data.setdefault("kills", 0)
    user_data.setdefault("rob", 0)

    if chat_id is not None:
        chat_id = int(chat_id)
        if chat_id not in user_data["groups"]:
            users_col.update_one(
                {"id": uid},
                {"$addToSet": {"groups": chat_id}}
            )
            user_data["groups"].append(chat_id)

    return user_data


def get_all_groups():
    groups = set()
    for u in users_col.find({}, {"groups": 1}):
        for g in u.get("groups", []):
            groups.add(int(g))
    return list(groups)


def get_all_users():
    return [int(u["id"]) for u in users_col.find({}, {"id": 1})]


def get_group_members(chat_id):
    return list(users_col.find({"groups": int(chat_id)}))


# =====================================================
# ================= RADHE EVENT SYSTEM =================
# =====================================================

def start_radhe_event(chat_id, multiplier, end_time):
    """
    end_time = unix timestamp (seconds)
    """
    settings_col.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {
            "radhe_event": {
                "active": True,
                "multiplier": int(multiplier),
                "end_time": float(end_time)
            }
        }},
        upsert=True
    )


def stop_radhe_event(chat_id):
    settings_col.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"radhe_event.active": False}},
        upsert=True
    )


def get_radhe_multiplier(chat_id):
    data = settings_col.find_one({"chat_id": int(chat_id)})
    if not data:
        return 1

    event = data.get("radhe_event")
    if not event or not event.get("active"):
        return 1

    if event.get("end_time", 0) < datetime.utcnow().timestamp():
        stop_radhe_event(chat_id)
        return 1

    return int(event.get("multiplier", 1))


# =====================================================
# ================= CLAIM SYSTEM =======================
# =====================================================

def is_group_claimed(chat_id):
    return groups_claim_col.find_one({"chat_id": int(chat_id)}) is not None


def mark_group_claimed(chat_id, user_id):
    groups_claim_col.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {
            "chat_id": int(chat_id),
            "claimed_by": int(user_id),
            "claimed_at": datetime.utcnow(),
        }},
        upsert=True
    )


# =====================================================
# ================= ECONOMY SYSTEM =====================
# =====================================================

def is_economy_on(chat_id):
    res = settings_col.find_one({"chat_id": int(chat_id)})
    return res.get("economy_status", True) if res else True


def set_economy_status(chat_id, status: bool):
    settings_col.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {"economy_status": bool(status)}},
        upsert=True
    )


# =====================================================
# ================= COUPLE SYSTEM ======================
# =====================================================

def get_couple(chat_id, date):
    return couples_col.find_one({"chat_id": int(chat_id), "date": date})


def save_couple(chat_id, date, couple_data):
    couples_col.update_one(
        {"chat_id": int(chat_id), "date": date},
        {"$set": {
            "chat_id": int(chat_id),
            "date": date,
            "c1_id": int(couple_data["c1_id"]),
            "c2_id": int(couple_data["c2_id"]),
            "image": couple_data["image"],
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )


# =====================================================
# ================= INDEXES ============================
# =====================================================

try:
    users_col.create_index("id", unique=True)
    settings_col.create_index("chat_id", unique=True)
    groups_claim_col.create_index("chat_id", unique=True)
    couples_col.create_index([("chat_id", 1), ("date", 1)], unique=True)
except Exception:
    pass
