from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database.db import get_user, users_col

# 👑 Bot Owner ID
OWNER_ID = 8432723762

# ====================== UTILS ======================
def is_owner(user_id: int):
    return user_id == OWNER_ID

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Target user find karne ke tareeke:
    1. Reply karke: /transfer 100
    2. Username se: /transfer 100 @username
    3. User ID se: /transfer 100 12345678
    """
    # 1. Agar reply kiya hai
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user

    # 2. Agar arguments diye hain (@username ya ID)
    if len(context.args) >= 2:
        target = context.args[1]
        
        # Username check
        if target.startswith("@"):
            try:
                chat = await context.bot.get_chat(target)
                return chat
            except Exception:
                return None
        
        # ID check
        try:
            uid = int(target)
            # MongoDB ke liye minimum structure
            class DummyUser:
                def __init__(self, id):
                    self.id = id
                    self.first_name = f"User_{id}"
            return DummyUser(uid)
        except ValueError:
            return None
            
    return None

# ====================== /transfer (Add Coins) ======================
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user

    if not is_owner(user_obj.id):
        return await update.message.reply_text("❌ Only bot owner can use this command.")

    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Usage: /transfer <amount> <reply/@user/id>")

    try:
        amount = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("❌ Amount ek number hona chahiye.")

    target_user_obj = await get_target_user(update, context)

    if not target_user_obj:
        return await update.message.reply_text("❌ Target user nahi mila. Reply karein ya @username/ID dein.")

    # MongoDB Update: $inc balance badhata hai. Upsert ensures entry exists.
    # get_user call karke naye user ko register karna zaroori hai
    get_user(target_user_obj) 
    
    result = users_col.update_one(
        {"id": target_user_obj.id},
        {"$inc": {"bal": amount}},
        upsert=True
    )

    if result.modified_count > 0 or result.upserted_id:
        await update.message.reply_text(
            f"✅ {target_user_obj.first_name} ko ${amount} coins add kar diye!"
        )
    else:
        # Agar already same data hai tab bhi success dikhayenge
        await update.message.reply_text(f"✅ ${amount} coins successfully processed for {target_user_obj.first_name}.")

# ====================== /remove (Subtract Coins) ======================
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_obj = update.effective_user

    if not is_owner(user_obj.id):
        return await update.message.reply_text("❌ Only bot owner can use this command.")

    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Usage: /remove <amount> <reply/@user/id>")

    try:
        amount = int(context.args[0])
    except ValueError:
        return await update.message.reply_text("❌ Amount ek number hona chahiye.")

    target_user_obj = await get_target_user(update, context)

    if not target_user_obj:
        return await update.message.reply_text("❌ Target user nahi mila.")

    # MongoDB Update: Negative amount se balance ghatayein
    users_col.update_one(
        {"id": target_user_obj.id},
        {"$inc": {"bal": -amount}},
        upsert=True
    )

    await update.message.reply_text(
        f"✅ {target_user_obj.first_name} se ${amount} coins remove kar diye!"
    )

# ====================== REGISTER ======================
def register_admin_commands(app):
    app.add_handler(CommandHandler("transfer", transfer))
    app.add_handler(CommandHandler("remove", remove))
