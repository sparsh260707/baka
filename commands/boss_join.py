from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
from config import BOT_USERNAME

async def join_group(update, context):
    if update.effective_chat.type == "private":
        return

    group_id = update.effective_chat.id
    link = f"https://t.me/{BOT_USERNAME}?start=bossjoin_{group_id}"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Join Boss Hunt", url=link)]
    ])

    await update.message.reply_text(
        "Boss hunt me register karne ke liye DM me join karo\n⏰ Deadline: 12:00 AM",
        reply_markup=kb
    )

def setup(app):
    app.add_handler(CommandHandler("join", join_group))
