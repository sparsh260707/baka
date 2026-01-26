# commands/sticker.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def sticker_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.effective_message.reply_to_message
    if not reply or not reply.sticker:
        return await update.effective_message.reply_text("📎 Reply to a sticker to get IDs.")
    st = reply.sticker
    await update.effective_message.reply_text(
        f"<b>Sticker ID:</b> <code>{st.file_id}</code>\n"
        f"<b>Unique ID:</b> <code>{st.file_unique_id}</code>",
        parse_mode="HTML"
    )


sticker_id_handler = CommandHandler(["stickerid", "stid"], sticker_id)
