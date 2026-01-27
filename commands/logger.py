# commands/logger.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from config import LOG_CHAT_ID
from database.db import users_col


print("✅ LOGGER MODULE LOADED")


# ===========================
# Track BOT status changes (added / removed / kicked)
# ===========================
async def bot_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.my_chat_member:
        return

    chat = update.effective_chat
    new = update.my_chat_member.new_chat_member.status
    old = update.my_chat_member.old_chat_member.status

    print("🔥 BOT STATUS UPDATE:", old, "->", new)

    # Bot added
    if old in ["left", "kicked"] and new in ["member", "administrator"]:

        users_col.update_many({}, {"$addToSet": {"groups": chat.id}})

        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"✅ <b>Bot added to group</b>\n\n"
                f"📝 {chat.title}\n"
                f"🆔 <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except:
            pass

    # Bot removed / kicked
    elif new in ["left", "kicked"]:

        users_col.update_many({}, {"$pull": {"groups": chat.id}})

        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"🚨 <b>Bot removed from group</b>\n\n"
                f"📝 {chat.title}\n"
                f"🆔 <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except:
            pass


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
    except:
        pass


# ===========================
# Register
# ===========================
def register_logger(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.MY_CHAT_MEMBER, bot_status_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.CHAT_MEMBER, bot_status_handler))

    # start logger should be LOW priority so main /start still works
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start"), start_logger), group=99)
