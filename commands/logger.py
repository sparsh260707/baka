from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ChatMemberHandler, MessageHandler, filters
from config import LOG_CHAT_ID

def nezuko_style(text):
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
    return str(text).lower().translate(mapping)

# --- 🚀 /START LOGGER ---
async def start_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type != "private":
        return
    user = update.effective_user
    msg = (
        f"🚀 <b>{nezuko_style('start used')}</b>\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 <code>{user.id}</code>"
    )
    try: await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
    except: pass

# --- ✅ BOT JOIN/LEAVE HANDLER ---
async def bot_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.my_chat_member
    chat = chat_member.chat
    new_status = chat_member.new_chat_member.status
    old_status = chat_member.old_chat_member.status
    user_who_added = chat_member.from_user

    if new_status in ["member", "administrator"] and old_status in ["kicked", "left"]:
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

# --- 👤 MEMBER JOIN/LEAVE HANDLER (FIXED) ---
async def member_activity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hum update.chat_member use karenge jo zyada reliable hai
    result = update.chat_member
    if not result: return

    chat = result.chat
    user = result.new_chat_member.user
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    # Check for Join
    if old_status in ["left", "kicked"] and new_status == "member":
        msg = (
            f"👤 <b>{nezuko_style('new member joined')}</b>\n\n"
            f"ɴᴀᴍᴇ: {user.full_name}\n"
            f"ɪᴅ: <code>{user.id}</code>\n"
            f"ɢʀᴏᴜᴘ: {chat.title}"
        )
        try: await context.bot.send_message(LOG_CHAT_ID, msg, parse_mode="HTML")
        except: pass

    # Check for Leave
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
    app.add_handler(CommandHandler("start", start_logger), group=1)
    
    # 1. Bot join/leave track karne ke liye
    app.add_handler(ChatMemberHandler(bot_status_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # 2. Users join/leave track karne ke liye (Ye important hai!)
    app.add_handler(ChatMemberHandler(member_activity_handler, ChatMemberHandler.CHAT_MEMBER))
