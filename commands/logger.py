# commands/logger.py

from telegram import Update, ChatMemberUpdated
from telegram.ext import (
    ContextTypes, MessageHandler, CommandHandler, ChatMemberHandler, filters
)
from config import LOG_CHAT_ID
from database.db import users_col


# ===========================
# New members joined
# ===========================
async def new_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat
    adder = update.effective_user

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            # Bot added
            users_col.update_many({}, {"$addToSet": {"groups": chat.id}})
            try:
                await context.bot.send_message(
                    LOG_CHAT_ID,
                    f"✅ <b>Bot added to group</b>\n\n"
                    f"📝 {chat.title}\n"
                    f"🆔 <code>{chat.id}</code>\n"
                    f"👤 Added by: {adder.mention_html()}",
                    parse_mode="HTML"
                )
            except Exception as e:
                print("Logger error (bot added):", e)

            try:
                await context.bot.send_message(chat.id, "🤖 Hello! Thanks for adding me ❤️")
            except:
                pass
        else:
            # Normal user joined
            try:
                await context.bot.send_message(
                    LOG_CHAT_ID,
                    f"👤 <b>New member joined</b>\n\n"
                    f"Name: {member.full_name}\n"
                    f"ID: <code>{member.id}</code>\n"
                    f"Group: {chat.title}",
                    parse_mode="HTML"
                )
            except Exception as e:
                print("Logger error (user join):", e)


# ===========================
# Members left
# ===========================
async def left_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.left_chat_member:
        return

    chat = update.effective_chat
    member = update.message.left_chat_member

    if member.id == context.bot.id:
        # Bot removed/kicked
        users_col.update_many({}, {"$pull": {"groups": chat.id}})
        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"🚨 <b>Bot removed/kicked from group</b>\n\n"
                f"📝 {chat.title}\n"
                f"🆔 <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Logger error (bot removed):", e)
    else:
        # Normal user left
        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"👤 <b>Member left</b>\n\n"
                f"Name: {member.full_name}\n"
                f"ID: <code>{member.id}</code>\n"
                f"Group: {chat.title}",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Logger error (user left):", e)


# ===========================
# Bot status (added/kicked) using ChatMemberHandler
# ===========================
async def bot_status_handler(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE):
    chat = update.chat
    new_status = update.chat_member.new_chat_member.status
    old_status = update.chat_member.old_chat_member.status

    if update.chat_member.new_chat_member.user.id != context.bot.id:
        return  # Only track bot

    if new_status in ["member", "administrator"] and old_status in ["kicked", "left"]:
        # Bot added
        users_col.update_many({}, {"$addToSet": {"groups": chat.id}})
        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"✅ <b>Bot added to group</b>\n\n📝 {chat.title}\n🆔 <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Logger error (bot status added):", e)

    elif new_status == "kicked":
        # Bot removed/kicked
        users_col.update_many({}, {"$pull": {"groups": chat.id}})
        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"🚨 <b>Bot removed/kicked from group</b>\n\n📝 {chat.title}\n🆔 <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Logger error (bot status removed):", e)


# ===========================
# /start logger (private)
# ===========================
async def start_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type != "private":
        return

    user = update.effective_user
    try:
        await context.bot.send_message(
            LOG_CHAT_ID,
            f"🚀 <b>/start used</b>\n\n"
            f"👤 {user.full_name}\n"
            f"🆔 <code>{user.id}</code>",
            parse_mode="HTML"
        )
    except Exception as e:
        print("Logger error (/start):", e)


# ===========================
# Register all handlers
# ===========================
def register_logger(app):
    # Users join/leave
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_members_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member_handler))

    # Bot status
    app.add_handler(ChatMemberHandler(bot_status_handler, ChatMemberHandler.MY_CHAT_MEMBER))

    # /start private
    app.add_handler(CommandHandler("start", start_logger), group=1)
