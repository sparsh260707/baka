# commands/logger.py

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler
from config import LOG_CHAT_ID

def nezuko_style(text):
    """Small Caps font for logger."""
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
    return str(text).lower().translate(mapping)

# --- 🚀 /START LOGGER (PRIVATE) ---
async def start_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type != "private":
        return
    user = update.effective_user
    msg = (
        f"🚀 <b>{nezuko_style('start used')}</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 <code>{user.id}</code>"
    )
    try:
        await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Logger Error (Start): {e}")

# --- ✅ BOT STATUS HANDLER (JOIN/KICK) ---
async def bot_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tracks when the bot itself is added or removed."""
    result = update.my_chat_member
    if not result: return

    chat = result.chat
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    user_who_acted = result.from_user

    # Case: Bot Added/Promoted
    if new_status in ["member", "administrator"] and old_status in ["left", "kicked"]:
        msg = (
            f"✅ <b>{nezuko_style('bot added to group')}</b>\n\n"
            f"📝 {chat.title}\n"
            f"🆔 <code>{chat.id}</code>\n"
            f"👤 {nezuko_style('added by')}: {user_who_acted.full_name}"
        )
        try:
            await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
            await context.bot.send_message(chat.id, "🤖 ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ʜᴇʀᴇ! ❤️")
        except: pass

    # Case: Bot Kicked/Left
    elif new_status in ["kicked", "left"]:
        msg = (
            f"🚨 <b>{nezuko_style('bot removed from group')}</b>\n\n"
            f"📝 {chat.title}\n"
            f"🆔 <code>{chat.id}</code>\n"
            f"👤 {nezuko_style('removed by')}: {user_who_acted.full_name}"
        )
        try:
            await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
        except: pass

# --- 👤 MEMBER ACTIVITY HANDLER (USER JOIN/LEAVE) ---
async def member_activity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tracks when users join or leave a group."""
    result = update.chat_member
    if not result: return

    chat = result.chat
    user = result.new_chat_member.user
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    if user.is_bot: return # Bots ko ignore karein

    # Case: User Joined
    if old_status in ["left", "kicked"] and new_status == "member":
        msg = (
            f"👤 <b>{nezuko_style('new member joined')}</b>\n\n"
            f"ɴᴀᴍᴇ: {user.full_name}\n"
            f"ɪᴅ: <code>{user.id}</code>\n"
            f"ɢʀᴏᴜᴘ: {chat.title}"
        )
        try: await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
        except: pass

    # Case: User Left/Kicked
    elif old_status == "member" and new_status in ["left", "kicked"]:
        msg = (
            f"👤 <b>{nezuko_style('member left')}</b>\n\n"
            f"ɴᴀᴍᴇ: {user.full_name}\n"
            f"ɪᴅ: <code>{user.id}</code>\n"
            f"ɢʀᴏᴜᴘ: {chat.title}"
        )
        try: await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
        except: pass

# --- 🛠️ REGISTRATION ---
def register_logger(app):
    # 1. Start command (Group 1 taaki main start ke sath conflict na ho)
    app.add_handler(CommandHandler("start", start_logger), group=1)
    
    # 2. Bot's own status (Kick/Join)
    app.add_handler(ChatMemberHandler(bot_status_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # 3. Members status (Join/Leave)
    app.add_handler(ChatMemberHandler(member_activity_handler, ChatMemberHandler.CHAT_MEMBER))
