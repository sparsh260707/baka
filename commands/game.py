import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import get_user, users_col, is_group_claimed, mark_group_claimed

# ====================== /claim ======================
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_obj = update.effective_user

    # Sirf groups mein chalega
    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ This command can only be used in a group.")

    # 1. Check if already claimed in this group (PERMANENT LOCK)
    if is_group_claimed(chat.id):
        return await update.message.reply_text("❌ Someone has already claimed the reward for this group!")

    # 2. Members count check karein
    try:
        members_count = await context.bot.get_chat_member_count(chat.id)
    except Exception as e:
        print(f"Error fetching members count: {e}")
        members_count = 0

    if members_count < 100:
        return await update.message.reply_text("❌ At least 100 members are required to claim the reward!")

    # 3. Reward Calculate aur Process
    reward = max(100, members_count // 10)
    
    # User register aur balance update (MongoDB Atomic $inc)
    get_user(user_obj, chat.id)
    users_col.update_one(
        {"id": user_obj.id},
        {"$inc": {"bal": reward}}
    )

    # 4. Iss group ko permanent block kar dein
    mark_group_claimed(chat.id, user_obj.id)

    await update.message.reply_text(
        f"✅ Success! You claimed the group reward of ${reward} coins!\n"
        f"⚠️ Ab iss group mein koi dobara claim nahi kar payega."
    )

# ====================== /daily ======================
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_obj = update.effective_user

    # Sirf Private chat (DM) mein
    if chat.type != "private":
        return await update.message.reply_text("⚠️ You can claim daily reward in DM only.")

    # MongoDB se user data fetch karein
    user_data = get_user(user_obj)
    
    now = int(time.time())
    last_claim = user_data.get("last_daily", 0)

    # 24 ghante ka check
    if now - last_claim < 86400:
        remaining = 86400 - (now - last_claim)
        next_time = str(timedelta(seconds=remaining)).split(".")[0] # Format: HH:MM:SS
        return await update.message.reply_text(
            f"⏳ You already claimed today's reward!\nTry again after {next_time}."
        )

    # Reward update aur timestamp set karein
    users_col.update_one(
        {"id": user_obj.id},
        {
            "$inc": {"bal": 1000},
            "$set": {"last_daily": now}
        }
    )

    await update.message.reply_text("✅ You received: $1000 daily reward!")

# ====================== REGISTER COMMANDS ======================
def register_game_commands(app):
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("daily", daily))
