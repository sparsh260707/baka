# Final Economy System for BAKA Bot - MongoDB Version
import time
import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import get_user, users_col, is_economy_on, set_economy_status

# ===== TIME UTILS =====
def now():
    return int(time.time())

# ===== USER HELPERS =====
def fancy_name(user):
    """Name safety check taaki UNKNOWN na aaye."""
    name = user.get("name", "Baka User").upper()
    return f"⏤͟͞ {name}"

def is_dead(user):
    return user.get("dead_until", 0) > now()

def is_protected(user):
    return user.get("protect_until", 0) > now()

async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is admin or creator of the group."""
    chat = update.effective_chat
    user_id = update.effective_user.id
    if chat.type == "private":
        return True
    try:
        member = await context.bot.get_chat_member(chat.id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

# ===== DATABASE HELPERS =====
def get_user_data(user_id, user_obj=None):
    if not user_obj:
        class Dummy: pass
        user_obj = Dummy()
        user_obj.id = user_id
        user_obj.first_name = f"User_{user_id}"
    return get_user(user_obj)

def update_user_data(user_id, user_data):
    users_col.replace_one({"id": user_id}, user_data)

def get_all_users():
    return list(users_col.find())

# ===== STATUS CHECK WRAPPER =====
async def can_use_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Economy system status aur admin bypass check karta hai."""
    chat_id = update.effective_chat.id
    is_open = is_economy_on(chat_id)
    is_admin = await is_user_admin(update, context)

    if not is_open and not is_admin:
        await update.message.reply_text("⚠️ For reopen use: /open")
        return False 
    return True

# ===== ADMIN COMMANDS: /open & /close =====
async def close_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_admin(update, context):
        return await update.message.reply_text("❌ Only admins can close the economy.")
    set_economy_status(update.effective_chat.id, False)
    await update.message.reply_text("✅ All economy commands have been disabled.")

async def open_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_admin(update, context):
        return await update.message.reply_text("❌ Only admins can open the economy.")
    set_economy_status(update.effective_chat.id, True)
    await update.message.reply_text("✅ All economy commands have been enabled.")

# ===== /bal =====
async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    user_obj = update.effective_user
    if update.message.reply_to_message:
        user_obj = update.message.reply_to_message.from_user
    user_data = get_user(user_obj)
    current_bal = user_data.get("bal", 0)
    status = "dead 💀" if is_dead(user_data) else "alive ❤️"
    text = f"👤 Name: {user_obj.first_name}\n💰 Balance: ${current_bal}\n🏆 Global Rank: 1\n❤️ Status: {status}"
    await update.message.reply_text(text)

# ===== /toprich =====
async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    all_users = get_all_users()
    all_users.sort(key=lambda x: x.get("bal", 0), reverse=True)
    msg = "🌍 Top 10 Richest Players:\n\n"
    for i, u in enumerate(all_users[:10], 1):
        name = u.get("name", "Unknown")
        msg += f"{i}. {name} — ${u.get('bal', 0)}\n"
    await update.message.reply_text(msg)

# ===== /rob =====
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to rob.")
    robber_user, victim_user = update.effective_user, update.message.reply_to_message.from_user
    robber, victim = get_user_data(robber_user.id, robber_user), get_user_data(victim_user.id, victim_user)
    if is_dead(robber): return await update.message.reply_text("❌ You are dead.")
    if is_protected(victim): return await update.message.reply_text("🛡️ Target is protected.")
    if victim.get("bal", 0) <= 0: return await update.message.reply_text("❌ Target has no money.")
    try:
        amount = int(context.args[0])
        if amount > victim.get("bal", 0): amount = victim.get("bal", 0)
    except: amount = victim.get("bal", 0)
    victim["bal"] -= amount
    robber["bal"] = robber.get("bal", 200) + amount
    update_user_data(robber_user.id, robber); update_user_data(victim_user.id, victim)
    await update.message.reply_text(f"👤 {fancy_name(robber)} robbed ${amount} from {victim_user.first_name}\n💰 Gained: ${amount}")

# ===== /kill =====
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to kill.")
    killer_user, victim_user = update.effective_user, update.message.reply_to_message.from_user
    killer, victim = get_user_data(killer_user.id, killer_user), get_user_data(victim_user.id, victim_user)
    if is_dead(killer): return await update.message.reply_text("❌ You are dead.")
    if is_dead(victim): return await update.message.reply_text("❌ Target is already dead.")
    if is_protected(victim): return await update.message.reply_text("🛡️ Target is protected.")
    victim["dead_until"] = now() + 5 * 60 * 60
    reward = random.randint(150, 170)
    killer["bal"] = killer.get("bal", 200) + reward
    killer["kills"] = killer.get("kills", 0) + 1
    update_user_data(killer_user.id, killer); update_user_data(victim_user.id, victim)
    await update.message.reply_text(f"👤 {fancy_name(killer)} killed {victim_user.first_name}!\n💰 Earned: ${reward}")

# ===== /revive =====
async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    reviver_user = update.effective_user
    reviver = get_user_data(reviver_user.id, reviver_user)
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else reviver_user
    target = get_user_data(target_user.id, target_user)
    if not is_dead(target): return await update.message.reply_text(f"✅ {target_user.first_name} is already alive!")
    if reviver.get("bal", 200) < 500: return await update.message.reply_text("❌ You need $500 to revive.")
    reviver["bal"] -= 500
    target["dead_until"] = 0
    update_user_data(reviver_user.id, reviver); update_user_data(target_user.id, target)
    msg = "❤️ You revived yourself! -$500" if reviver_user.id == target_user.id else f"❤️ {fancy_name(reviver)} revived {target_user.first_name}! -$500"
    await update.message.reply_text(msg)

# ===== /protect =====
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    user = get_user_data(update.effective_user.id, update.effective_user)
    if not context.args or context.args[0] not in ["1d", "2d", "3d"]:
        return await update.message.reply_text("⚠️ Usage: /protect 1d/2d/3d")
    days = context.args[0]
    costs = {"1d": 200, "2d": 500, "3d": 800}
    if user.get("bal", 200) < costs[days]: return await update.message.reply_text(f"❌ You need ${costs[days]} to protect.")
    user["bal"] -= costs[days]
    user["protect_until"] = now() + int(days[0]) * 24 * 60 * 60
    update_user_data(update.effective_user.id, user)
    await update.message.reply_text(f"🛡️ You are now protected for {days}.")

# ===== /give =====
async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Reply to someone: /give <amount>")
    giver_user, receiver_user = update.effective_user, update.message.reply_to_message.from_user
    giver, receiver = get_user_data(giver_user.id, giver_user), get_user_data(receiver_user.id, receiver_user)
    try: amount = int(context.args[0])
    except: return await update.message.reply_text("❌ Invalid amount.")
    if giver.get("bal", 200) < amount: return await update.message.reply_text("❌ Insufficient funds.")
    giver["bal"] -= amount
    receiver["bal"] = receiver.get("bal", 200) + amount
    update_user_data(giver_user.id, giver); update_user_data(receiver_user.id, receiver)
    await update.message.reply_text(f"💰 {giver.get('name', 'Giver')} gave ${amount} to {receiver.get('name', 'Receiver')}")

# ===== /myrank & /leaders =====
async def myrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    all_users = get_all_users()
    all_users.sort(key=lambda x: x.get("bal", 0), reverse=True)
    rank = next((i for i, u in enumerate(all_users, 1) if u.get("id") == update.effective_user.id), 1)
    await update.message.reply_text(f"🏆 Your global rank is {rank}")

async def leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): return
    all_users = get_all_users()
    all_users.sort(key=lambda x: x.get("kills", 0), reverse=True)
    msg = "🔥 Top 10 Bomb Game Players:\n\n"
    for i, u in enumerate(all_users[:10], 1): msg += f"{i}. {u.get('name', 'User')} — {u.get('kills', 0)} kills\n"
    await update.message.reply_text(msg)

# ===== /economy =====
async def economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """⚡️ Baka Bot Economy Guide

📌 User Commands:
/bal, /toprich, /rob, /kill, /protect, /revive, /give, /myrank, /leaders

👑 Admin Commands:
/open — Everyone can use economy
/close — Only admins can use economy"""
    await update.message.reply_text(msg)
