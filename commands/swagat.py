# commands/swagat.py

from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_user, users_col

REWARD = 500

# ===== When new member joins =====
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.new_chat_members:
        return

    chat = update.effective_chat

    for user in update.message.new_chat_members:
        # Ignore bots
        if user.is_bot:
            continue

        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

        text = (
            f"👋 {mention}\n\n"
            f"🎁 <b>Swagat likho aur {REWARD} coins pao!</b>\n"
            f"👉 Type: /swagat"
        )

        await update.message.reply_text(text, parse_mode="HTML")


# ===== /swagat command =====
async def swagat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    user_data = get_user(user)

    # Already claimed
    if user_data.get("swagat_claimed", False):
        return await update.message.reply_text("❌ Swagat already claimed!")

    # Give reward
    user_data["bal"] = user_data.get("bal", 0) + REWARD
    user_data["swagat_claimed"] = True

    users_col.replace_one({"id": user.id}, user_data, upsert=True)

    # Group welcome message
    text = (
        f"🌸 {mention}\n\n"
        f"✨ <b>SWAGAT HAI AAPKA HAMARE GROUP ME</b>\n"
        f"🏷 <b>{chat.title}</b>\n\n"
        f"🙏 <b>RADHE RADHE</b>\n"
        f"🎁 Aapko <b>{REWARD} coins</b> mile!"
    )

    await update.message.reply_text(text, parse_mode="HTML")
