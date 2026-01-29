import time
from telegram import Update, ChatMember
from telegram.ext import ContextTypes, CommandHandler

from config import OWNER_ID
from database.db import (
    start_radhe_event,
    stop_radhe_event,
    get_radhe_multiplier,
    get_all_groups
)

# ================= CONFIG =================
ADMIN_EVENT_DURATION = 10 * 60   # 10 minutes
OWNER_EVENT_MULTIPLIER = 2
ADMIN_EVENT_MULTIPLIER = 2
# ==========================================


# =====================================================
# /radhe command
# =====================================================
async def radhe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ Group only command.")

    now = int(time.time())

    # ---------------- BOT OWNER (GLOBAL EVENT) ----------------
    if user.id == OWNER_ID:
        if not context.args:
            return await update.message.reply_text(
                "Usage: /radhe <minutes>\nExample: /radhe 30"
            )

        try:
            minutes = int(context.args[0])
        except:
            return await update.message.reply_text("❌ Invalid time.")

        end_time = now + (minutes * 60)

        groups = get_all_groups()
        for gid in groups:
            start_radhe_event(gid, OWNER_EVENT_MULTIPLIER, end_time)

        await update.message.reply_text(
            f"🔥 RADHE EVENT STARTED (GLOBAL)\n"
            f"⏱ Duration: {minutes} minutes\n"
            f"💰 All rewards are now 2×"
        )
        return

    # ---------------- GROUP ADMIN (10 MIN ONLY) ----------------
    member = await chat.get_member(user.id)
    if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        return await update.message.reply_text("❌ Admins only.")

    current = get_radhe_multiplier(chat.id)
    if current > 1:
        return await update.message.reply_text(
            "⚠️ RADHE event already active in this group."
        )

    end_time = now + ADMIN_EVENT_DURATION
    start_radhe_event(chat.id, ADMIN_EVENT_MULTIPLIER, end_time)

    await update.message.reply_text(
        "🔥 RADHE EVENT ACTIVATED!\n"
        "⏱ Duration: 10 minutes\n"
        "💰 All coins & rewards are now 2×"
    )


# =====================================================
# /radheoff (OWNER ONLY)
# =====================================================
async def radheoff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id != OWNER_ID:
        return await update.message.reply_text("❌ Owner only command.")

    groups = get_all_groups()
    for gid in groups:
        stop_radhe_event(gid)

    await update.message.reply_text("🛑 RADHE EVENT STOPPED (GLOBAL)")


# =====================================================
# REGISTER
# =====================================================
def register_radhe(app):
    app.add_handler(CommandHandler("radhe", radhe))
    app.add_handler(CommandHandler("radheoff", radheoff))
