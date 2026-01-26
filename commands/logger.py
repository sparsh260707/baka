# commands/logger.py
import os
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters

LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", 0))


# ===========================
# Bot added to new group
# ===========================
async def log_new_group(chat_title, chat_id, added_by=None, context: ContextTypes.DEFAULT_TYPE = None):
    text = f"📩 Bot added to a new group!\n\n" \
           f"📝 Group: {chat_title}\n" \
           f"🆔 Group ID: <code>{chat_id}</code>"
    if added_by:
        text += f"\n👤 Added by: {added_by.mention_html()}"
    if context:
        try:
            await context.bot.send_message(LOG_CHAT_ID, text, parse_mode="HTML")
        except Exception as e:
            print(f"❌ Failed to log new group: {e}")


async def new_group_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type in ["group", "supergroup"]:
        await log_new_group(chat.title, chat.id, added_by=user, context=context)
        try:
            await context.bot.send_message(chat.id, "🤖 Hello! I'm your friendly bot. Thanks for adding me! 💕")
        except:
            pass


# ===========================
# New member join logging
# ===========================
async def new_member_logger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    new_members = update.message.new_chat_members
    for member in new_members:
        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"👤 New member joined:\nName: {member.full_name}\nID: <code>{member.id}</code>\nGroup: {chat.title} (<code>{chat.id}</code>)",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"❌ Failed to log new member: {e}")


# ===========================
# Private start logging
# ===========================
async def log_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    try:
        await context.bot.send_message(
            LOG_CHAT_ID,
            f"🚀 Bot started by user!\n👤 Name: {user.full_name}\n🆔 ID: <code>{user.id}</code>\nChat Type: {chat.type}",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"❌ Failed to log /start: {e}")


# ===========================
# Register all handlers
# ===========================
def register_logger(app):
    # New group detection
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_group_handler))
    
    # New member join logging
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member_logger))
    
    # /start logging
    app.add_handler(CommandHandler("start", log_start_command))
