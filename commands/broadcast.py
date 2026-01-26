# commands/broadcast.py

import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest

from database.db import users_col


# ===== CONFIG =====
SUDO_USERS = {123456789}  # 👈 apna Telegram ID daal yaha


# ===== BROADCAST =====
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        return

    args = context.args
    reply = update.message.reply_to_message

    if not args and not reply:
        return await update.message.reply_text(
            "📢 <b>Broadcast Usage</b>\n\n"
            "/broadcast -user (reply to message)\n"
            "/broadcast -group (reply to message)\n\n"
            "Flags:\n"
            "-clean = copy message",
            parse_mode=ParseMode.HTML
        )

    target_type = "user" if "-user" in args else "group" if "-group" in args else None
    if not target_type:
        return await update.message.reply_text("❌ Use -user or -group flag")

    is_clean = "-clean" in args

    msg_text = None
    if not reply:
        clean_args = [a for a in args if a not in ["-user", "-group", "-clean"]]
        if not clean_args:
            return await update.message.reply_text("❌ Reply or give text")
        msg_text = " ".join(clean_args)

    status = await update.message.reply_text(f"⏳ Broadcasting to {target_type}s...")

    sent = 0
    failed = 0

    # ===== COLLECT TARGETS =====
    targets = set()

    if target_type == "user":
        for u in users_col.find({}, {"id": 1}):
            if "id" in u:
                targets.add(u["id"])
    else:
        for u in users_col.find({}, {"groups": 1}):
            for g in u.get("groups", []):
                targets.add(g)

    # ===== SEND =====
    for cid in targets:
        try:
            if reply:
                if is_clean:
                    await reply.copy(cid)
                else:
                    await reply.forward(cid)
            else:
                await context.bot.send_message(cid, msg_text, parse_mode=ParseMode.HTML)

            sent += 1
            if sent % 20 == 0:
                await asyncio.sleep(1)

        except (Forbidden, BadRequest):
            # ❌ Remove dead group/user from DB
            users_col.update_many({}, {"$pull": {"groups": cid}})
            failed += 1

        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ <b>Broadcast Finished</b>\n\n"
        f"📤 Sent: {sent}\n"
        f"❌ Failed: {failed}",
        parse_mode=ParseMode.HTML
    )


# ===== REGISTER =====
def register_broadcast(app):
    app.add_handler(CommandHandler("broadcast", broadcast))
