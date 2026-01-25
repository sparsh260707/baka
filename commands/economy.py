import time
import random
from telegram import Update
from telegram.ext import ContextTypes

# ========= DATABASE =========

DB_FILE = "database.json"

import json

def load():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def now():
    return int(time.time())

# ========= USER SYSTEM =========

def get_user(data, tg_user):
    uid = str(tg_user.id)
    if uid not in data:
        data[uid] = {
            "id": uid,
            "name": tg_user.first_name,
            "bal": 0,
            "kills": 0,
            "dead_until": 0,
            "protect_until": 0,
            "last_salary": 0
        }
    return data[uid]

def fancy_name(user):
    return f"⏤͟͞ {user.first_name.upper()}"

def is_dead(u):
    return u["dead_until"] > now()

def is_protected(u):
    return u["protect_until"] > now()

def salary(u):
    if now() - u["last_salary"] >= 12 * 60 * 60:
        u["bal"] += 50
        u["last_salary"] = now()

# ========= COMMANDS =========

# /bal
async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    else:
        target_user = update.effective_user

    u = get_user(data, target_user)
    salary(u)

    all_users = list(data.values())
    all_users.sort(key=lambda x: x["bal"], reverse=True)
    rank = all_users.index(u) + 1

    status = "dead" if is_dead(u) else "alive"

    msg = f"""👤 Name: {target_user.first_name}
💰 Balance: ${u['bal']}
🏆 Global Rank: {rank}
❤️ Status: {status}
⚔️ Kills: {u['kills']}"""

    save(data)
    await update.message.reply_text(msg)

# /rob
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to rob.")

    data = load()

    robber_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    robber = get_user(data, robber_user)
    victim = get_user(data, victim_user)

    if is_dead(robber):
        return await update.message.reply_text("❌ You are dead.")

    if is_dead(victim):
        return await update.message.reply_text("❌ This user is already dead.")

    if is_protected(victim):
        return await update.message.reply_text("🛡️ This user is protected.")

    if victim["bal"] <= 0:
        return await update.message.reply_text("❌ This user has no money.")

    amount = min(victim["bal"], random.randint(10, 100))
    gained = int(amount * 0.9)

    victim["bal"] -= amount
    robber["bal"] += gained

    save(data)

    msg = f"""👤 {fancy_name(robber_user)} robbed ${amount} from {victim_user.first_name}
💰 gained: ${gained}"""
    await update.message.reply_text(msg)

# /kill
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to kill.")

    data = load()

    killer_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    killer = get_user(data, killer_user)
    victim = get_user(data, victim_user)

    if is_dead(killer):
        return await update.message.reply_text("❌ You are dead.")

    if is_dead(victim):
        return await update.message.reply_text("❌ This user is already dead.")

    if is_protected(victim):
        return await update.message.reply_text("🛡️ This user is protected.")

    victim["dead_until"] = now() + 5 * 60 * 60

    reward = random.randint(50, 200)
    killer["bal"] += reward
    killer["kills"] += 1

    save(data)

    msg = f"""👤 {fancy_name(killer_user)} killed {victim_user.first_name}!
💰 Earned: ${reward}"""
    await update.message.reply_text(msg)

# /revive
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()

    reviver_user = update.effective_user
    reviver = get_user(data, reviver_user)

    # self revive
    if not update.message.reply_to_message:
        if not is_dead(reviver):
            return await update.message.reply_text(
                f"✅ {fancy_name(reviver_user)} is already alive!"
            )

        if reviver["bal"] < 500:
            return await update.message.reply_text("❌ You need $500 to revive.")

        reviver["bal"] -= 500
        reviver["dead_until"] = 0
        save(data)
        return await update.message.reply_text("❤️ You revived yourself! -$500")

    # revive other
    target_user = update.message.reply_to_message.from_user
    target = get_user(data, target_user)

    if not is_dead(target):
        return await update.message.reply_text(
            f"✅ {fancy_name(target_user)} is already alive!"
        )

    if reviver["bal"] < 500:
        return await update.message.reply_text("❌ You need $500 to revive.")

    reviver["bal"] -= 500
    target["dead_until"] = 0

    save(data)

    msg = f"❤️ {fancy_name(reviver_user)} revived {target_user.first_name}! -$500"
    await update.message.reply_text(msg)

# /protect
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()
    user = update.effective_user
    u = get_user(data, user)

    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /protect 1d")

    days = context.args[0]

    if days != "1d":
        return await update.message.reply_text("❌ Only 1d protection allowed.")

    if u["bal"] < 200:
        return await update.message.reply_text("❌ You need $200.")

    u["bal"] -= 200
    u["protect_until"] = now() + 24 * 60 * 60

    save(data)

    await update.message.reply_text("🛡️ You are now protected for 1d.")
