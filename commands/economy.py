import time
import random
from telegram import Update
from telegram.ext import ContextTypes
from database.db import load, save, get_user  # Correct import

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

# ===== /bal =====
async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    user = get_user_data(target_user.id)

    # Set starting balance to 200 if new
    if "bal" not in user:
        user["bal"] = 200

    # Calculate rank
    all_users = get_user_data(all_users=True)  # fetch all users from db
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

# ===== /rob =====
async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to rob.")

    robber_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    robber = get_user_data(robber_user.id)
    victim = get_user_data(victim_user.id)

    if is_dead(robber):
        return await update.message.reply_text("❌ You are dead.")
    if is_dead(victim):
        return await update.message.reply_text("❌ Target is dead.")
    if is_protected(victim):
        return await update.message.reply_text("🛡️ Target is protected.")
    if victim.get("bal", 0) <= 0:
        return await update.message.reply_text("❌ Target has no money.")

    amount = min(victim.get("bal", 0), random.randint(10, 100))  # steal <= victim balance
    robber["bal"] = robber.get("bal", 200) + amount
    victim["bal"] -= amount

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

    reward = random.randint(150, 170)  # kill reward between 150-170
    killer["bal"] = killer.get("bal", 200) + reward
    killer["kills"] = killer.get("kills", 0) + 1

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

    if reviver.get("bal", 200) < 500:
        return await update.message.reply_text("❌ You need $500 to revive.")

    reviver["bal"] -= 500
    target["dead_until"] = 0

    update_user_data(reviver_user.id, reviver)
    update_user_data(target_user.id, target)

    if target_user.id == reviver_user.id:
        msg = "❤️ You revived yourself! -$500"
    else:
        msg = f"❤️ {fancy_name(reviver)} revived {target_user.first_name}! -$500"
    await update.message.reply_text(msg)

# ===== /protect =====
async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user_data(update.effective_user.id)

    if not context.args or context.args[0] != "1d":
        return await update.message.reply_text("⚠️ Usage: /protect 1d (only 1d allowed)")

    if user.get("bal", 200) < 200:
        return await update.message.reply_text("❌ You need $200 to protect.")

    user["bal"] -= 200
    user["protect_until"] = now() + 24 * 60 * 60

    update_user_data(update.effective_user.id, user)
    await update.message.reply_text("🛡️ You are now protected for 1 day!")
