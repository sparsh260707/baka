# commands/admin.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import load, save, get_user

# 👑 PUT YOUR TELEGRAM USER ID HERE
OWNER_ID = 8432723762  # <-- apna Telegram ID daalo

# ====================== UTILS ======================
def is_owner(user_id: int):
    return user_id == OWNER_ID

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Target user find karne ke 3 tareeke:
    1. Reply karke command
    2. /transfer 100 @username
    3. /transfer 100 user_id
    """

    # 1️⃣ If reply
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user

    # 2️⃣ If username or id in args
    if len(context.args) >= 2:
        target = context.args[1]

        # Username
        if target.startswith("@"):
            try:
                user = await context.bot.get_chat(target)
                return user
            except:
                return None

        # User ID
        try:
            uid = int(target)
            class DummyUser:
                def __init__(self, id):
                    self.id = id
                    self.first_name = f"User_{id}"

            return DummyUser(uid)
        except:
            return None

    return None

# ====================== /transfer ======================
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user

    if not is_owner(user_obj.id):
        await update.message.reply_text("❌ Only bot owner can use this command.")
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "/transfer <amount> <user>\n"
            "Ya kisi user ko reply karke:\n"
            "/transfer <amount>"
        )
        return

    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("❌ Amount number hona chahiye.")
        return

    target_user_obj = await get_target_user(update, context)

    if not target_user_obj:
        await update.message.reply_text("❌ User not found. Reply karo ya @username / user_id do.")
        return

    data = load()
    target_user = get_user(data, target_user_obj)

    target_user["bal"] = target_user.get("bal", 0) + amount
    save(data)

    await update.message.reply_text(
        f"✅ {target_user_obj.first_name} ko ${amount} coins add kar diye!"
    )

# ====================== /remove ======================
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user

    if not is_owner(user_obj.id):
        await update.message.reply_text("❌ Only bot owner can use this command.")
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "/remove <amount> <user>\n"
            "Ya kisi user ko reply karke:\n"
            "/remove <amount>"
        )
        return

    try:
        amount = int(context.args[0])
    except:
        await update.message.reply_text("❌ Amount number hona chahiye.")
        return

    target_user_obj = await get_target_user(update, context)

    if not target_user_obj:
        await update.message.reply_text("❌ User not found. Reply karo ya @username / user_id do.")
        return

    data = load()
    target_user = get_user(data, target_user_obj)

    target_user["bal"] = max(0, target_user.get("bal", 0) - amount)
    save(data)

    await update.message.reply_text(
        f"✅ {target_user_obj.first_name} se ${amount} coins remove kar diye!"
    )

# ====================== REGISTER ======================
def register_admin_commands(app):
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("remove", remove))
