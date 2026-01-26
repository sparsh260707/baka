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
        return await update.message.reply_text("❌ You are not allowed to use this.")

    args = context.args
    reply = update.message.reply_to_message

    if not reply and not args:
        return await update.message.reply_text(
            "📢 <b>Broadcast Usage:</b>\n\n"
            "➤ Reply karke: <code>/broadcast</code>\n"
            "➤ Ya: <code>/broadcast Hello</code>",
            parse_mode=ParseMode.HTML
        )

    status = await update.message.reply_text("⏳ Broadcasting to users & groups...")

    sent = 0
    failed = 0

    # =====================
    # Collect ALL targets
    # =====================
    targets = set()

    for u in users_col.find({}):
        uid = u.get("id")
        if uid:
            targets.add(uid)

        for gid in u.get("groups", []):
            targets.add(gid)

    # =====================
    # Send broadcast
    # =====================
    for cid in targets:
        try:
            if reply:
                await reply.copy(chat_id=cid)
            else:
                await context.bot.send_message(cid, " ".join(args))
            sent += 1

            if sent % 20 == 0:
                await asyncio.sleep(1)

        except Forbidden:
            failed += 1
        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"📤 Sent: <code>{sent}</code>\n"
        f"❌ Failed: <code>{failed}</code>\n"
        f"📦 Total Targets: <code>{len(targets)}</code>",
        parse_mode=ParseMode.HTML
    )

def register_broadcast(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
