# commands/logger.py

import os
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters

# Put your LOG GROUP ID in .env
# Example: LOG_CHAT_ID=-1001234567890
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "0"))


# ===========================
# /start logging (private)
# ===========================
async def log_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.effective_user

    try:
        await context.bot.send_message(
            chat_id=LOG_CHAT_ID,
            text=(
                "🚀 <b>Bot Started</b>\n\n"
                f"👤 Name: {user.full_name}\n"
                f"🆔 ID: <code>{user.id}</code>\n"
                f"🔗 Username: @{user.username if user.username else 'None'}"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Failed to log /start: {e}")


# ===========================
# New members & bot added
# ===========================
async def new_chat_members_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.message

    if not message or not message.new_chat_members:
        return

    for member in message.new_chat_members:

        # =======================
        # If BOT is added
        # =======================
        if member.id == context.bot.id:
            added_by = message.from_user

            text = (
                "➕ <b>Bot Added To New Group</b>\n\n"
                f"📛 Group: {chat.title}\n"
                f"🆔 Group ID: <code>{chat.id}</code>\n"
            )

            if added_by:
                text += (
                    f"\n👤 Added by: {added_by.full_name}"
                    f"\n🆔 User ID: <code>{added_by.id}</code>"
                )

            try:
                await context.bot.send_message(LOG_CHAT_ID, text, parse_mode="HTML")
            except Exception as e:
                print(f"❌ Failed to log new group: {e}")

            # Optional welcome in group
            try:
                await context.bot.send_message(
                    chat.id,
                    "🤖 Hello! Thanks for adding me 💕"
                )
            except:
                pass

        # =======================
        # Normal member joined
        # =======================
        else:
            try:
                await context.bot.send_message(
                    LOG_CHAT_ID,
                    (
                        "👤 <b>New Member Joined</b>\n\n"
                        f"👤 Name: {member.full_name}\n"
                        f"🆔 ID: <code>{member.id}</code>\n"
                        f"📛 Group: {chat.title}\n"
                        f"🆔 Group ID: <code>{chat.id}</code>"
                    ),
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"❌ Failed to log new member: {e}")


# ===========================
# Register logger
# ===========================
def register_logger(app):
    # /start logger
    app.add_handler(CommandHandler("start", log_start_command), group=1)

    # New members & bot added
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_members_logger),
        group=1
    )
