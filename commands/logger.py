# commands/logger.py

import os
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters
from telegram.error import Forbidden, BadRequest

from database.db import users_col

LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", -1003471039882))


# ===========================
# Bot added to new group
# ===========================
async def log_new_group(chat_title, chat_id, added_by=None, context: ContextTypes.DEFAULT_TYPE = None):
    if not LOG_CHAT_ID:
        return

    text = (
        "📩 <b>Bot added to new group</b>\n\n"
        f"📝 Group: {chat_title}\n"
        f"🆔 Group ID: <code>{chat_id}</code>"
    )
    if added_by:
        text += f"\n👤 Added by: {added_by.mention_html()}"

    try:
        await context.bot.send_message(LOG_CHAT_ID, text, parse_mode="HTML")
    except:
        pass


async def new_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    chat = update.effective_chat
    user = update.effective_user

    if not msg or not msg.new_chat_members:
        return

    for member in msg.new_chat_members:
        if member.id == context.bot.id:
            await log_new_group(chat.title, chat.id, user, context)

            try:
                await context.bot.send_message(chat.id, "🤖 Hello! Thanks for adding me ❤️")
            except:
                pass


# ===========================
# New member join logging
# ===========================
async def new_member_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not LOG_CHAT_ID:
        return

    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            continue

        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"👤 <b>New member joined</b>\n\n"
                f"Name: {member.full_name}\n"
                f"ID: <code>{member.id}</code>\n"
                f"Group: {chat.title} (<code>{chat.id}</code>)",
                parse_mode="HTML"
            )
        except:
            pass


# ===========================
# Bot kicked / left group
# ===========================
async def bot_left_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not LOG_CHAT_ID:
        return

    msg = update.message
    chat = update.effective_chat

    if not msg or not msg.left_chat_member:
        return

    member = msg.left_chat_member

    if member.id == context.bot.id:
        # 🧹 Remove group from DB
        users_col.update_many({}, {"$pull": {"groups": chat.id}})

        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"🚨 <b>Bot removed from group</b>\n\n"
                f"📝 Group: {chat.title}\n"
                f"🆔 ID: <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except:
            pass


# ===========================
# Private start logging
# ===========================
async def log_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not LOG_CHAT_ID:
        return

    user = update.effective_user
    chat = update.effective_chat

    try:
        await context.bot.send_message(
            LOG_CHAT_ID,
            f"🚀 <b>Bot started</b>\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"Chat: {chat.type}",
            parse_mode="HTML"
        )
    except:
        pass


# ===========================
# Register all handlers
# ===========================
def register_logger(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_group_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_logger))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, bot_left_logger))
    app.add_handler(CommandHandler("start", log_start_command))
