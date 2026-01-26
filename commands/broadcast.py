# commands/broadcast.py
import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from telegram.error import Forbidden

from baka.utils import SUDO_USERS
from database.db import users_col

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        return

    args = context.args
    reply = update.message.reply_to_message

    if not reply and not args:
        return await update.message.reply_text(
            "📢 <b>Broadcast Usage:</b>\n\n"
            "➤ Reply karke: <code>/broadcast</code>\n"
            "➤ Ya: <code>/broadcast Hello users</code>",
            parse_mode=ParseMode.HTML
        )

    status = await update.message.reply_text("⏳ Broadcasting...")

    users = users_col.find({})
    sent = 0
    failed = 0

    for u in users:
        uid = u.get("id")
        try:
            if reply:
                await reply.copy(chat_id=uid)
            else:
                await context.bot.send_message(uid, " ".join(args))
            sent += 1
            if sent % 20 == 0:
                await asyncio.sleep(1)
        except Forbidden:
            users_col.delete_one({"id": uid})
            failed += 1
        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ <b>Broadcast Done!</b>\n\n"
        f"📤 Sent: <code>{sent}</code>\n"
        f"❌ Failed: <code>{failed}</code>",
        parse_mode=ParseMode.HTML
    )

def register_broadcast(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
