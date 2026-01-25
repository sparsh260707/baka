import time, random
from telegram import Update
from telegram.ext import ContextTypes
from database.db import load, save, get_user

# ================= HELPERS =================

def is_dead(u):
    return time.time() < u["dead_until"]

def is_protected(u):
    return time.time() < u["protect_until"]

def salary(u):
    if time.time() - u["last_salary"] > 12 * 3600:
        u["bal"] += 50
        u["last_salary"] = time.time()

def fancy_name(user):
    return f"⏤͟͞ {user.first_name.upper()}"

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()
    get_user(data, update.effective_user)
    save(data)
    await update.message.reply_text("🎮 Economy Crime Game Started!\nType /economy")

async def economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
📖 Economy Commands:
/bal
/rob (reply)
/kill (reply)
/revive
/protect 1d
/give (reply) amount
/toprich
""")

# ============ /bal ============

async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()
    u = get_user(data, update.effective_user)
    salary(u)

    all_users = list(data.values())
    all_users.sort(key=lambda x: x["bal"], reverse=True)
    rank = all_users.index(u) + 1

    status = "dead" if is_dead(u) else "alive"

    msg = f"""👤 Name: {update.effective_user.first_name}
💰 Balance: ${u['bal']}
🏆 Global Rank: {rank}
❤️ Status: {status}
⚔️ Kills: {u['kills']}"""

    save(data)
    await update.message.reply_text(msg)

# ============ /rob ============

async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to rob.")

    data = load()

    robber_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    robber = get_user(data, robber_user)
    victim = get_user(data, victim_user)

    salary(robber)

    if is_dead(robber):
        return await update.message.reply_text("☠️ You are dead.")

    if is_protected(victim):
        return await update.message.reply_text("🛡️ Victim is protected right now!")

    if victim["bal"] < 1:
        return await update.message.reply_text("Target is too poor 😂")

    steal = random.randint(1, victim["bal"])
    gain = int(steal * 0.9)

    victim["bal"] -= steal
    robber["bal"] += gain
    robber["rob"] += 1

    save(data)

    msg = f"""👤 {fancy_name(robber_user)} robbed ${steal} from {victim_user.first_name}
💰 gained: ${gain}"""

    await update.message.reply_text(msg)

# ============ /kill ============

async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to kill.")

    data = load()

    killer_user = update.effective_user
    victim_user = update.message.reply_to_message.from_user

    killer = get_user(data, killer_user)
    victim = get_user(data, victim_user)

    if is_protected(victim):
        return await update.message.reply_text("🛡️ Victim is protected right now!")

    reward = random.randint(50, 200)

    victim["dead_until"] = time.time() + 5 * 3600
    killer["kills"] += 1
    killer["bal"] += reward

    save(data)

    msg = f"""👤 {fancy_name(killer_user)} killed {victim_user.first_name}!
💰 Earned: ${reward}"""

    await update.message.reply_text(msg)

# ============ /revive ============

async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()

    reviver_user = update.effective_user
    reviver = get_user(data, reviver_user)

    if reviver["bal"] < 500:
        return await update.message.reply_text("❌ You need $500 to revive.")

    # self revive
    if not update.message.reply_to_message:
        reviver["bal"] -= 500
        reviver["dead_until"] = 0
        save(data)
        return await update.message.reply_text("❤️ You revived yourself! -$500")

    # revive other
    target_user = update.message.reply_to_message.from_user
    target = get_user(data, target_user)

    reviver["bal"] -= 500
    target["dead_until"] = 0

    save(data)

    msg = f"❤️ {fancy_name(reviver_user)} revived {target_user.first_name}! -$500"
    await update.message.reply_text(msg)

# ============ /protect ============

async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /protect 1d")

    if context.args[0] != "1d":
        return await update.message.reply_text("⚠️ Only 1d protection is available.")

    data = load()
    u = get_user(data, update.effective_user)

    cost = 200

    if u["bal"] < cost:
        return await update.message.reply_text("❌ Not enough money!")

    u["bal"] -= cost
    u["protect_until"] = time.time() + 86400

    save(data)

    await update.message.reply_text("🛡️ You are now protected for 1d.")

# ============ /give ============

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Reply and give amount.")

    try:
        amt = int(context.args[0])
    except:
        return await update.message.reply_text("Invalid amount.")

    data = load()
    u1 = get_user(data, update.effective_user)
    u2 = get_user(data, update.message.reply_to_message.from_user)

    if u1["bal"] < amt:
        return await update.message.reply_text("Not enough money.")

    u1["bal"] -= amt
    u2["bal"] += amt

    save(data)
    await update.message.reply_text("🎁 Money sent!")

# ============ /toprich ============

async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()

    top = sorted(data.values(), key=lambda x: x["bal"], reverse=True)[:10]

    msg = "🌍 Top 10 Richest:\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u['name']} — ${u['bal']}\n"

    await update.message.reply_text(msg)
