import time, random
from telegram import Update
from telegram.ext import ContextTypes
from database.db import load, save, get_user

# ---------- HELPERS ----------

def is_dead(u):
    return time.time() < u["dead_until"]

def is_protected(u):
    return time.time() < u["protect_until"]

def salary(u):
    if time.time() - u["last_salary"] > 12*3600:
        u["bal"] += 50
        u["last_salary"] = time.time()

# ---------- COMMANDS ----------

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
/protect 1d/2d/3d
/give (reply) amount
/toprich
""")

async def bal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()
    u = get_user(data, update.effective_user)
    salary(u)
    save(data)
    await update.message.reply_text(f"💰 Balance: ${u['bal']}")

async def rob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to rob.")

    data = load()
    robber = get_user(data, update.effective_user)
    victim = get_user(data, update.message.reply_to_message.from_user)

    salary(robber)

    if is_dead(robber):
        return await update.message.reply_text("☠️ You are dead.")
    if is_protected(victim):
        return await update.message.reply_text("🛡️ Target is protected!")

    if victim["bal"] < 10:
        return await update.message.reply_text("Target is too poor 😂")

    amt = random.randint(1, min(200, victim["bal"]))
    victim["bal"] -= amt
    robber["bal"] += amt
    robber["rob"] += 1

    save(data)
    await update.message.reply_text(f"🦹 You robbed ${amt}!")

async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to kill.")

    data = load()
    killer = get_user(data, update.effective_user)
    victim = get_user(data, update.message.reply_to_message.from_user)

    if is_protected(victim):
        return await update.message.reply_text("🛡️ Target is protected!")

    victim["dead_until"] = time.time() + 5*3600
    killer["kills"] += 1

    save(data)
    await update.message.reply_text("💀 Target killed for 5 hours!")

async def revive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()
    if update.message.reply_to_message:
        u = get_user(data, update.message.reply_to_message.from_user)
    else:
        u = get_user(data, update.effective_user)

    u["dead_until"] = 0
    save(data)
    await update.message.reply_text("❤️ Revived!")

async def protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("/protect 1d / 2d / 3d")

    data = load()
    u = get_user(data, update.effective_user)

    prices = {"1d":200, "2d":500, "3d":800}

    d = context.args[0]
    if d not in prices:
        return await update.message.reply_text("Use: 1d / 2d / 3d")

    if u["bal"] < prices[d]:
        return await update.message.reply_text("Not enough money!")

    u["bal"] -= prices[d]
    u["protect_until"] = time.time() + int(d[0]) * 86400

    save(data)
    await update.message.reply_text("🛡️ Protection activated!")

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not context.args:
        return await update.message.reply_text("Reply and give amount.")

    try:
        amt = int(context.args[0])
    except:
        return await update.message.reply_text("Invalid amount")

    data = load()
    u1 = get_user(data, update.effective_user)
    u2 = get_user(data, update.message.reply_to_message.from_user)

    if u1["bal"] < amt:
        return await update.message.reply_text("Not enough money.")

    u1["bal"] -= amt
    u2["bal"] += amt

    save(data)
    await update.message.reply_text("🎁 Money sent!")

async def toprich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load()

    top = sorted(data.values(), key=lambda x: x["bal"], reverse=True)[:10]

    msg = "🌍 Top 10 Richest:\n"
    for i, u in enumerate(top, 1):
        msg += f"{i}. {u['name']} — ${u['bal']}\n"

    await update.message.reply_text(msg)
