import time
from datetime import datetime, timedelta
from telegram import Update, ChatMember
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from database.db import (
    # user
    get_user,
    users_col,

    # group economy
    get_user_data,
    update_user_data,
    get_group_data,
    update_group_data,

    # claim system
    is_group_claimed,
    mark_group_claimed
)

# ================== CONFIG ==================
OWNER_JOIN_BONUS = 1000

DAILY_MSG_TARGET = 100
DAILY_GROUP_REWARD = 500
DAILY_USER_REWARD = 100
# ============================================


# =====================================================
# 1️⃣ BOT ADDED → GROUP JOIN BONUS
# =====================================================
async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        return

    group = get_group_data(chat.id)
    if group.get("joined_bonus_given"):
        return

    admins = await chat.get_administrators()
    owner = next((a.user for a in admins if a.status == ChatMember.OWNER), None)

    if owner:
        owner_data = get_user_data(owner.id, owner)
        owner_data["bal"] += OWNER_JOIN_BONUS
        update_user_data(owner.id, owner_data)

    group.update({
        "wallet": group.get("wallet", 0) + 500,
        "joined_bonus_given": True,
        "daily_msgs": 0,
        "reward_given": False,
        "last_reset": datetime.utcnow()
    })

    update_group_data(chat.id, group)


# =====================================================
# 2️⃣ DAILY GROUP ACTIVITY TRACK
# =====================================================
async def track_group_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    group = get_group_data(chat.id)
    now = datetime.utcnow()

    # daily reset
    if now - group.get("last_reset", now) > timedelta(days=1):
        group["daily_msgs"] = 0
        group["reward_given"] = False
        group["last_reset"] = now

    group["daily_msgs"] += 1

    if group["daily_msgs"] >= DAILY_MSG_TARGET and not group["reward_given"]:
        group["wallet"] = group.get("wallet", 0) + DAILY_GROUP_REWARD
        group["reward_given"] = True

        user = get_user_data(update.effective_user.id, update.effective_user)
        user["bal"] += DAILY_USER_REWARD
        update_user_data(update.effective_user.id, user)

        await update.message.reply_text(
            f"🎉 Daily activity completed!\n"
            f"🏦 Group +{DAILY_GROUP_REWARD}\n"
            f"👤 You +{DAILY_USER_REWARD}"
        )

    update_group_data(chat.id, group)


# =====================================================
# 3️⃣ GROUP WALLET
# =====================================================
async def group_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ Group only command.")

    group = get_group_data(chat.id)
    await update.message.reply_text(
        f"🏦 Group Wallet: {group.get('wallet', 0)} 💰"
    )


async def give_from_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        return

    member = await chat.get_member(user.id)
    if member.status not in ["administrator", "creator"]:
        return await update.message.reply_text("❌ Admins only.")

    if len(context.args) != 2 or not update.message.entities:
        return await update.message.reply_text("Usage: /givedp @user amount")

    target = update.message.entities[1].user

    try:
        amount = int(context.args[1])
    except:
        return await update.message.reply_text("❌ Invalid amount.")

    group = get_group_data(chat.id)
    if group.get("wallet", 0) < amount:
        return await update.message.reply_text("❌ Insufficient group balance.")

    target_data = get_user_data(target.id, target)
    target_data["bal"] += amount
    group["wallet"] -= amount

    update_user_data(target.id, target_data)
    update_group_data(chat.id, group)

    await update.message.reply_text(
        f"✅ {amount} coins given to {target.first_name}"
    )


# =====================================================
# 4️⃣ /claim (ONE TIME GROUP)
# =====================================================
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        return await update.message.reply_text("❌ Group only command.")

    if is_group_claimed(chat.id):
        return await update.message.reply_text(
            "❌ This group is already claimed permanently."
        )

    try:
        members = await context.bot.get_chat_member_count(chat.id)
    except:
        return await update.message.reply_text("❌ Cannot fetch members count.")

    if members < 100:
        return await update.message.reply_text(
            "❌ Minimum 100 members required."
        )

    reward = members * 3

    get_user(user, chat.id)
    users_col.update_one(
        {"id": user.id},
        {"$inc": {"bal": reward}},
        upsert=True
    )

    mark_group_claimed(chat.id, user.id)

    await update.message.reply_text(
        f"✅ Group Claimed!\n"
        f"👥 Members: {members}\n"
        f"💰 Reward: {reward}"
    )


# =====================================================
# 5️⃣ /daily (DM ONLY)
# =====================================================
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type != "private":
        return await update.message.reply_text(
            "⚠️ Use this command in DM only."
        )

    data = get_user(user)
    now = int(time.time())
    last = data.get("last_daily", 0)

    if now - last < 86400:
        left = 86400 - (now - last)
        time_left = str(timedelta(seconds=left)).split(".")[0]
        return await update.message.reply_text(
            f"⏳ Already claimed.\nTry after {time_left}"
        )

    users_col.update_one(
        {"id": user.id},
        {"$inc": {"bal": 1000}, "$set": {"last_daily": now}},
        upsert=True
    )

    await update.message.reply_text("✅ Daily reward: 1000 coins")


# =====================================================
# REGISTER
# =====================================================
def register_game_commands(app):
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("groupbal", group_balance))
    app.add_handler(CommandHandler("givedp", give_from_group))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, track_group_activity))
