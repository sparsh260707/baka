# commands/broadcast.py

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.error import Forbidden

from baka.utils import SUDO_USERS
from database import db


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        return

    args = context.args
    reply = update.message.reply_to_message

    if not args and not reply:
        return await update.message.reply_text(
            "📢 <b>Broadcast Manager</b>\n\n"
            "<b>Usage:</b>\n"
            "‣ /broadcast -user (Reply to msg)\n"
            "‣ /broadcast -group (Reply to msg)\n\n"
            "<b>Flags:</b>\n"
            "‣ -clean : Copy msg (Use for Buttons)",
            parse_mode=ParseMode.HTML
        )

    target_type = "user" if "-user" in args else "group" if "-group" in args else None
    if not target_type:
        return await update.message.reply_text(
            "⚠️ Missing flag: <code>-user</code> or <code>-group</code>",
            parse_mode=ParseMode.HTML
        )

    is_clean = "-clean" in args

    msg_text = None
    if not reply:
        clean_args = [a for a in args if a not in ["-user", "-group", "-clean"]]
        if not clean_args:
            return await update.message.reply_text("⚠️ Give me a message or reply to one.", parse_mode=ParseMode.HTML)
        msg_text = " ".join(clean_args)

    status_msg = await update.message.reply_text(
        f"⏳ <b>Broadcasting to {target_type}s...</b>",
        parse_mode=ParseMode.HTML
    )

    count = 0

    if target_type == "user":
        targets = db.users.find({})
    else:
        targets = db.groups.find({})

    for doc in targets:
        cid = doc.get("user_id") if target_type == "user" else doc.get("chat_id")

        try:
            if reply:
                if is_clean:
                    await reply.copy(cid)
                else:
                    await reply.forward(cid)
            else:
                await context.bot.send_message(chat_id=cid, text=msg_text, parse_mode=ParseMode.HTML)

            count += 1
            if count % 20 == 0:
                await asyncio.sleep(1)

        except Forbidden:
            if target_type == "user":
                db.users.delete_one({"user_id": cid})
            else:
                db.groups.delete_one({"chat_id": cid})
        except Exception:
            pass

    await status_msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\nSent to {count} {target_type}s.",
        parse_mode=ParseMode.HTML
    )
