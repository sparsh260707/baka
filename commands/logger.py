# commands/logger.py

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, filters

from config import LOG_CHAT_ID
from database.db import users_col


# ===========================
# When bot is added to group
# ===========================
async def new_members_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    chat = update.effective_chat
    adder = update.effective_user

    for member in update.message.new_chat_members:

        # 🤖 Bot added
        if member.id == context.bot.id:

            print("BOT ADDED TO:", chat.id)  # debug

            # Save group in DB
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
                print("Logger error (add):", e)

            try:
                await context.bot.send_message(chat.id, "🤖 Hello! Thanks for adding me ❤️")
            except:
                pass


# ===========================
# When bot removed / kicked
# ===========================
async def left_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.left_chat_member:
        return

    chat = update.effective_chat
    member = update.message.left_chat_member

    # 🤖 Bot removed
    if member.id == context.bot.id:

        print("BOT REMOVED FROM:", chat.id)  # debug

        # Remove group from DB
        users_col.update_many({}, {"$pull": {"groups": chat.id}})

        try:
            await context.bot.send_message(
                LOG_CHAT_ID,
                f"🚨 <b>Bot removed from group</b>\n\n"
                f"📝 {chat.title}\n"
                f"🆔 <code>{chat.id}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            print("Logger error (remove):", e)


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
# Register
# ===========================
def register_logger(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_members_handler))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member_handler))
    app.add_handler(CommandHandler("start", start_logger), group=1)
