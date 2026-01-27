# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL STABLE LOGGER - ALL ERRORS FIXED

from telegram import Update, ChatMemberUpdated
from telegram.ext import (
    ContextTypes, MessageHandler, CommandHandler, ChatMemberHandler, filters
)
from config import LOG_CHAT_ID
from database.db import users_col

def nezuko_style(text):
    """Simple Small Caps font for logger."""
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
    return str(text).lower().translate(mapping)

# --- 🚀 /START LOGGER (PRIVATE) ---
async def start_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type != "private":
        return
    user = update.effective_user
    msg = (
        f"🚀 <b>/start used</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 <code>{user.id}</code>"
    )
    try:
        await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
    except: pass

# --- ✅ BOT JOIN/LEAVE & STATUS HANDLER (FIXED ATTRIBUTE ERROR) ---
async def bot_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tracks when the bot is added or removed from a group."""
    # FIX: update.chat_member se data nikalna padta hai
    chat_member = update.chat_member
    chat = chat_member.chat
    new_status = chat_member.new_chat_member.status
    old_status = chat_member.old_chat_member.status
    user_who_added = chat_member.from_user

    # Bot added to a new group
    if new_status in ["member", "administrator"] and old_status in ["kicked", "left"]:
        users_col.update_many({}, {"$addToSet": {"groups": chat.id}})
        msg = (
            f"✅ <b>{nezuko_style('bot added to group')}</b>\n\n"
            f"📝 {chat.title}\n"
            f"🆔 <code>{chat.id}</code>\n"
            f"👤 {nezuko_style('added by')}: {user_who_added.full_name}"
        )
        try:
            await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
            await context.bot.send_message(chat.id, "🤖 ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ʜᴇʀᴇ! ❤️")
        except: pass

    # Bot removed or kicked
    elif new_status in ["kicked", "left"]:
        users_col.update_many({}, {"$pull": {"groups": chat.id}})
        msg = (
            f"🚨 <b>{nezuko_style('bot removed from group')}</b>\n\n"
            f"📝 {chat.title}\n"
            f"🆔 <code>{chat.id}</code>"
        )
        try:
            await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
        except: pass

# --- 👤 MEMBER JOIN/LEAVE HANDLER ---
async def member_activity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tracks normal users joining or leaving."""
    if not update.message: return
    chat = update.effective_chat
    
    # New Member Joined
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.id == context.bot.id: continue
            msg = (
                f"👤 <b>{nezuko_style('new member joined')}</b>\n\n"
                f"ɴᴀᴍᴇ: {member.full_name}\n"
                f"ɪᴅ: <code>{member.id}</code>\n"
                f"ɢʀᴏᴜᴘ: {chat.title}"
            )
            try: await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
            except: pass

    # Member Left
    elif update.message.left_chat_member:
        member = update.message.left_chat_member
        if member.id == context.bot.id: return
        msg = (
            f"👤 <b>{nezuko_style('member left')}</b>\n\n"
            f"ɴᴀᴍᴇ: {member.full_name}\n"
            f"ɪᴅ: <code>{member.id}</code>\n"
            f"ɢʀᴏᴜᴘ: {chat.title}"
        )
        try: await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
        except: pass

# --- 🛠️ REGISTRATION ---
def register_logger(app):
    app.add_handler(CommandHandler("start", start_logger), group=1)
    # ChatMemberHandler me update pass hota hai, chat nahi
    app.add_handler(ChatMemberHandler(bot_status_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.StatusUpdate.ALL, member_activity_handler))
