import time
from datetime import timedelta
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import (
    get_user,
    users_col,
    is_group_claimed,
    mark_group_claimed
)

# ====================== /claim ======================
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_obj = update.effective_user

    # Sirf groups mein chalega
    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text(
            "❌ This command can only be used in a group."
        )

    # 1. Check if already claimed in this group (PERMANENT LOCK)
    if is_group_claimed(chat.id):
        return await update.message.reply_text(
            "❌ Someone has already claimed the reward for this group!"
        )

    # 2. Members count check
    try:
        members_count = await context.bot.get_chat_member_count(chat.id)
    except Exception as e:
        print(f"Error fetching members count: {e}")
        members_count = 0

    if members_count < 100:
        return await update.message.reply_text(
            "❌ At least 100 members are required to claim the reward!"
        )

    # 3. Reward calculation
    # 1 member = 3 coins
    reward = members_count * 3

    # 4. User register + balance update
    get_user(user_obj, chat.id)
    users_col.update_one(
        {"id": user_obj.id},
        {"$inc": {"bal": reward}}
    )

    # 5. Group ko permanently claimed mark karo
    mark_group_claimed(chat.id, user_obj.id)

    await update.message.reply_text(
        f"✅ Success!\n\n"
        f"👥 Group Members: {members_count}\n"
        f"💰 Reward: {reward} coins\n\n"
        f"⚠️ Is group me ab dobara claim nahi ho sakta."
    )


# ====================== /daily ======================
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_obj = update.effective_user

    # Sirf private chat (DM) mein
    if chat.type != "private":
        return await update.message.reply_text(
            "⚠️ You can claim daily reward in DM only."
        )

    # User data fetch
    user_data = get_user(user_obj)

    now = int(time.time())
    last_claim = user_data.get("last_daily", 0)

    # 24 hours cooldown check
    if now - last_claim < 86400:
        remaining = 86400 - (now - last_claim)
        next_time = str(timedelta(seconds=remaining)).split(".")[0]
        return await update.message.reply_text(
            f"⏳ You already claimed today's reward!\n"
            f"Try again after {next_time}."
        )

    # Reward update
    users_col.update_one(
        {"id": user_obj.id},
        {
            "$inc": {"bal": 1000},
            "$set": {"last_daily": now}
        }
    )

    await update.message.reply_text(
        "✅ You received: 1000 coins as daily reward!"
    )


# ====================== REGISTER COMMANDS ======================
def register_game_commands(app):
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("daily", daily))
