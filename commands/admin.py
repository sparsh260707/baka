from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import get_user, users_col

# 👑 Bot Owner ID
OWNER_ID = 8432723762

# ====================== UTILS ======================
def is_owner(user_id: int):
    return user_id == OWNER_ID

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Target user find karne ke tareeke (Reply, @username, user_id)."""
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user

    if len(context.args) >= 2:
        target = context.args[1]
        if target.startswith("@"):
            try:
                chat = await context.bot.get_chat(target)
                return chat
            except:
                return None
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

# ====================== /transfer (Add Coins) ======================
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user

    if not is_owner(user_obj.id):
        return await update.message.reply_text("❌ Only bot owner can use this command.")

    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Usage: /transfer <amount> <user/reply>")

    try:
        amount = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Amount number hona chahiye.")

    target_user_obj = await get_target_user(update, context)

    if not target_user_obj:
        return await update.message.reply_text("❌ User not found.")

    # MongoDB Update: $inc use karke coins badhayein
    get_user(target_user_obj) # Ensure user exists in DB
    users_col.update_one(
        {"id": target_user_obj.id},
        {"$inc": {"bal": amount}}
    )

    await update.message.reply_text(
        f"✅ {target_user_obj.first_name} ko ${amount} coins add kar diye!"
    )

# ====================== /remove (Subtract Coins) ======================
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user

    if not is_owner(user_obj.id):
        return await update.message.reply_text("❌ Only bot owner can use this command.")

    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Usage: /remove <amount> <user/reply>")

    try:
        amount = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Amount number hona chahiye.")

    target_user_obj = await get_target_user(update, context)

    if not target_user_obj:
        return await update.message.reply_text("❌ User not found.")

    # MongoDB Update: Balance se coins ghatayein
    # Note: Hum negative value pass kar rahe hain subtract karne ke liye
    users_col.update_one(
        {"id": target_user_obj.id},
        {"$inc": {"bal": -amount}}
    )

    await update.message.reply_text(
        f"✅ {target_user_obj.first_name} se ${amount} coins remove kar diye!"
    )

# ====================== REGISTER ======================
def register_admin_commands(app):
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("remove", remove))
