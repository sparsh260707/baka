from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_members = update.message.new_chat_members
    chat = update.effective_chat

    for user in new_members:
        # Clickable name style
        welcome_text = f"😉 Welcome - <a href='tg://user?id={user.id}'>{user.first_name}</a>"

        # Optional: Add a button (e.g., rules or group link)
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("➕ Join Group", url=f"https://t.me/{context.bot.username}?startgroup=true")
        ]])

        await update.message.reply_text(
            welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
