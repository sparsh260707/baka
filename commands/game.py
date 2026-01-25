# commands/game.py
import time
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import load, save, get_user

DB_FILE = "database/users.json"

# ====================== /claim ======================
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_obj = update.effective_user

    # Only in group
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command can only be used in a group.")
        return

    # Fetch members count safely
    try:
        members_count = await context.bot.get_chat_member_count(chat.id)
    except Exception as e:
        print(f"Error fetching members count: {e}")
        members_count = 0

    if members_count < 100:
        await update.message.reply_text("❌ At least 100 members are required to claim the reward!")
        return

    # Load database
    data = load()
    user = get_user(data, user_obj)  # ensures user exists in DB

    # Dynamic reward: 1 coin per 10 members, minimum 100
    reward = max(100, members_count // 10)

    user["bal"] = user.get("bal", 200) + reward
    save(data)

    await update.message.reply_text(f"✅ You claimed the group reward of ${reward} coins!")

# ====================== /daily ======================
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_obj = update.effective_user

    # Only in private chat
    if chat.type != "private":
        await update.message.reply_text("⚠️ You can claim daily reward in DM only.")
        return

    data = load()
    user = get_user(data, user_obj)

    now = int(time.time())
    last_claim = user.get("last_daily", 0)

    if now - last_claim < 86400:  # 24 hours = 86400 seconds
        next_time = datetime.fromtimestamp(last_claim + 86400).strftime("%I:%M %p IST")
        await update.message.reply_text(
            f"⏳ You already claimed today's reward!\nCome back after {next_time}."
        )
        return

    # Give daily reward
    user["bal"] = user.get("bal", 0) + 1000
    user["last_daily"] = now
    save(data)

    await update.message.reply_text("✅ You received: $1000 daily reward!")

# ====================== REGISTER COMMANDS ======================
def register_game_commands(app):
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("daily", daily))
