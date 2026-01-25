from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import get_user, users_col

OWNER_ID = 8432723762

def is_owner(user_id: int):
    return user_id == OWNER_ID

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user

    if len(context.args) >= 2:
        target = context.args[1]
        if target.startswith("@"):
            try:
                chat = await context.bot.get_chat(target)
                return chat
            except: return None
        try:
            uid = int(target)
            class DummyUser:
                def __init__(self, id):
                    self.id = id
                    self.first_name = f"User_{id}"
                    self.name = f"User_{id}" # Added this safety
            return DummyUser(uid)
        except: return None
    return None

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user
    if not is_owner(user_obj.id):
        return await update.message.reply_text("❌ Only bot owner can use this.")

    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Usage: /transfer <amount> <reply/@user/id>")

    try:
        amount = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Amount invalid hai.")

    target_user_obj = await get_target_user(update, context)
    if not target_user_obj:
        return await update.message.reply_text("❌ User nahi mila.")

    # MongoDB Update
    get_user(target_user_obj) 
    users_col.update_one(
        {"id": target_user_obj.id},
        {"$inc": {"bal": amount}},
        upsert=True
    )

    # Use getattr to prevent 'name' or 'first_name' errors
    name = getattr(target_user_obj, 'first_name', "User")
    await update.message.reply_text(f"✅ {name} ko ${amount} coins add kar diye!")

async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user
    if not is_owner(user_obj.id):
        return await update.message.reply_text("❌ Only bot owner can use this.")

    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Usage: /remove <amount>")

    try:
        amount = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Amount invalid.")

    target_user_obj = await get_target_user(update, context)
    if not target_user_obj:
        return await update.message.reply_text("❌ User not found.")

    users_col.update_one(
        {"id": target_user_obj.id},
        {"$inc": {"bal": -amount}},
        upsert=True
    )

    name = getattr(target_user_obj, 'first_name', "User")
    await update.message.reply_text(f"✅ {name} se ${amount} coins remove kar diye!")

def register_admin_commands(app):
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("remove", remove))
