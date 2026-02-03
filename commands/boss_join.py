from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
from config import BOT_USERNAME
from database.boss import register_user


# =========================
# GROUP HANDLER: /join
# =========================
async def join_group(update, context):
    # Sirf group me kaam kare
    if update.effective_chat.type == "private":
        return

    group_id = update.effective_chat.id

    # Deep-link with group_id
    link = f"https://t.me/{BOT_USERNAME}?start=bossjoin_{group_id}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Join Boss Hunt", url=link)]
    ])

    await update.message.reply_text(
        "Boss hunt me register karne ke liye DM me join karo\n"
        "⏰ Deadline: 12:00 AM",
        reply_markup=keyboard
    )


# =========================
# DM HANDLER: /start bossjoin_xxx
# =========================
async def start_dm(update, context):
    # Sirf private chat
    if update.effective_chat.type != "private":
        return

    if not context.args:
        return

    arg = context.args[0]
    if not arg.startswith("bossjoin_"):
        return

    try:
        group_id = int(arg.split("_", 1)[1])
    except ValueError:
        return

    user = update.effective_user

    ok = register_user(
        user_id=user.id,
        username=user.username,
        group_id=group_id
    )

    if not ok:
        await update.message.reply_text(
            "❌ Registration closed ho chuki hai ya tum already join ho."
        )
        return

    await update.message.reply_text(
        "✅ Tum Boss Hunt ke liye register ho gaye ho.\n"
        "⏳ Kal isi group me boss spawn hoga.\n"
        "Good luck!"
    )


# =========================
# SETUP (IMPORTANT)
# =========================
def setup(app):
    app.add_handler(CommandHandler("join", join_group))
    app.add_handler(CommandHandler("start", start_dm))
