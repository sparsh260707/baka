# commands/economy.py
# Final Economy System for BAKA Bot
# Handles /bal, /rob, /kill, /revive, /protect, /give, /myrank, /toprich, /leaders, /economy

import time
import random
from telegram import Update
from telegram.ext import ContextTypes
from database.db import load, save, get_user

# ===== TIME UTILS =====
def now():
    return int(time.time())

# ===== USER HELPERS =====
def fancy_name(user):
    return f"⏤͟͞ {user['name'].upper()}"

def is_dead(user):
    return user.get("dead_until", 0) > now()

def is_protected(user):
    return user.get("protect_until", 0) > now()

# ===== DATABASE HELPERS =====
def get_user_data(user_id):
    data = load()
    for u_id, u in data.items():
        if u_id == str(user_id):
            return u
    # If not found, create new user
    dummy_user = type("Dummy", (), {"id": user_id, "first_name": "User"})()
    user = get_user(data, dummy_user)
    save(data)
    return user

def update_user_data(user_id, user):
    data = load()
    data[str(user_id)] = user
    save(data)

def get_all_users():
    return list(load().values())

# ===== /bal =====
async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    user = get_user_data(target_user.id)

    if "bal" not in user:
        user["bal"] = 200

    all_users = get_all_users()
    all_users.sort(key=lambda x: x.get("bal", 0), reverse=True)
    rank = all_users.index(user) + 1 if user in all_users else 1

    status = "dead" if is_dead(user) else "alive"
    msg = f"""👤 Name: {target_user.first_name}
💰 Balance: ${user['bal']}
🏆 Global Rank: {rank}
❤️ Status: {status}
⚔️ Kills: {user.get('kills', 0)}"""
    update_user_data(target_user.id, user)
    await update.message.reply_text(msg)

# ===== /toprich =====
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_users = get_all_users()
    all_users.sort(key=lambda x: x.get("bal",0), reverse=True)
    msg = "🌍 Top 10 Richest Players:\n\n"
    for i, u in enumerate(all_users[:10],1):
        msg += f"{i}. {u['name']} — ${u.get('bal',0)}\n"
    await update.message.reply_text(msg)

# ===== /rob =====
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to rob.")

    robber_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    robber = get_user_data(robber_user.id)
    victim = get_user_data(victim_user.id)

    # Only robber sees their status messages
    if is_dead(robber):
        return await update.message.reply_text("❌ You are dead.")
    if is_dead(victim):
        return await update.message.reply_text("❌ Target is dead.")
    if is_protected(victim):
        return await update.message.reply_text("🛡️ Target is protected.")
    if victim.get("bal", 0) <= 0:
        return await update.message.reply_text("❌ Target has no money.")

    # Optional amount
    try:
        amount = int(context.args[0])
        if amount > victim.get("bal",0):
            amount = victim.get("bal",0)
    except:
        amount = victim.get("bal",0)  # default: steal all

    victim["bal"] -= amount
    robber["bal"] = robber.get("bal",200) + amount

    update_user_data(robber_user.id, robber)
    update_user_data(victim_user.id, victim)

    msg = f"👤 {fancy_name(robber)} robbed ${amount} from {victim_user.first_name}\n💰 Gained: ${amount}"
    await update.message.reply_text(msg)

# ===== /kill =====
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to kill.")

    killer_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    killer = get_user_data(killer_user.id)
    victim = get_user_data(victim_user.id)

    if is_dead(killer):
        return await update.message.reply_text("❌ You are dead.")
    if is_dead(victim):
        return await update.message.reply_text("❌ Target is already dead.")
    if is_protected(victim):
        return await update.message.reply_text("🛡️ Target is protected.")

    victim["dead_until"] = now() + 5 * 60 * 60  # 5 hours

    reward = random.randint(150, 170)
    killer["bal"] = killer.get("bal",200) + reward
    killer["kills"] = killer.get("kills",0) + 1

    update_user_data(killer_user.id, killer)
    update_user_data(victim_user.id, victim)

    msg = f"👤 {fancy_name(killer)} killed {victim_user.first_name}!\n💰 Earned: ${reward}"
    await update.message.reply_text(msg)

# ===== /revive =====
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reviver_user = update.effective_user
    reviver = get_user_data(reviver_user.id)

    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else reviver_user
    target = get_user_data(target_user.id)

    if not is_dead(target):
        return await update.message.reply_text(f"✅ {target_user.first_name} is already alive!")

    if reviver.get("bal",200)<500:
        return await update.message.reply_text("❌ You need $500 to revive.")

    reviver["bal"] -= 500
    target["dead_until"] = 0

    update_user_data(reviver_user.id, reviver)
    update_user_data(target_user.id, target)

    msg = "❤️ You revived yourself! -$500" if reviver_user.id==target_user.id else f"❤️ {fancy_name(reviver)} revived {target_user.first_name}! -$500"
    await update.message.reply_text(msg)

# ===== /protect =====
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)

    if not context.args or context.args[0] not in ["1d","2d","3d"]:
        return await update.message.reply_text("⚠️ Usage: /protect 1d/2d/3d")

    days = context.args[0]
    costs = {"1d":200,"2d":500,"3d":800}

    if user.get("bal",200)<costs[days]:
        return await update.message.reply_text(f"❌ You need ${costs[days]} to protect.")

    user["bal"] -= costs[days]
    user["protect_until"] = now() + int(days[0])*24*60*60
    update_user_data(update.effective_user.id,user)
    await update.message.reply_text(f"🛡️ You are now protected for {days}.")

# ===== /give =====
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Reply to someone and specify amount: /give <amount>")

    giver = get_user_data(update.effective_user.id)
    receiver = get_user_data(update.message.reply_to_message.from_user)

    try:
        amount = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Invalid amount.")

    if giver.get("bal",200)<amount:
        return await update.message.reply_text("❌ You don't have enough money.")

    giver["bal"] -= amount
    receiver["bal"] = receiver.get("bal",200)+amount

    update_user_data(update.effective_user.id,giver)
    update_user_data(update.message.reply_to_message.from_user.id,receiver)
    await update.message.reply_text(f"💰 {giver['name']} gave ${amount} to {receiver['name']}")

# ===== /myrank =====
async def myrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)
    all_users = get_all_users()
    all_users.sort(key=lambda x:x.get("bal",0),reverse=True)
    rank = all_users.index(user)+1 if user in all_users else 1
    await update.message.reply_text(f"🏆 Your global rank is {rank}")

# ===== /leaders =====
async def leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_users = get_all_users()
    all_users.sort(key=lambda x:x.get("kills",0),reverse=True)
    msg = "🔥 Top 10 Bomb Game Players:\n\n"
    for i,u in enumerate(all_users[:10],1):
        msg += f"{i}. {u['name']} — {u.get('kills',0)} kills\n"
    await update.message.reply_text(msg)

# ===== /economy =====
async def economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """⚡️ All users get $50 every 12 hours!

📌 Commands:
/bal — Your/your friend's balance 💵
/toprich — Top 10 richest globally 🌍
/rob (reply) <amount> — Rob money 🦹‍♂️
/kill (reply) — Kill someone 💀
/protect <1d/2d/3d> — Protect yourself 🛡️
/revive (reply or no reply) — Revive yourself or a friend ❤️
/give (reply) <amount> — Give money 🎁
/myrank — Show global bomb rank 🏆
/leaders - Show top 10 bomb game players
/economy — Full economy guide 📖

🔒 Protection Rules:
Protected users cannot be robbed or killed.
Dead users auto-revive after 5 hours, or use /revive to come back sooner.
1-day = $200 💰 | 2-day = $500 💰| 3-day = $800 💰

⚠️ Note: All virtual money, fun only! 🎉"""
    await update.message.reply_text(msg)
