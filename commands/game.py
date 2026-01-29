import time
from datetime import datetime, timedelta

from telegram import Update, ChatMember
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

from database.db import (
    get_user,
    users_col,

    get_group_data,
    update_group_data,
    get_user_data,
    update_user_data,

    is_group_claimed,
    mark_group_claimed
)

# ================== CONFIG ==================
OWNER_JOIN_BONUS = 1000

DAILY_MSG_TARGET = 100
DAILY_GROUP_REWARD = 500
DAILY_USER_REWARD = 100

DAILY_RESET_HOURS = 24
# ============================================


# =====================================================
# INTERNAL HELPERS
# =====================================================

def _utcnow():
    return datetime.utcnow()


def _need_reset(last_reset: datetime):
    if not last_reset:
        return True
    return (_utcnow() - last_reset) >= timedelta(hours=DAILY_RESET_HOURS)


# =====================================================
# 1️⃣ BOT ADDED → GROUP JOIN BONUS
# =====================================================
async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
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
        "reward_user": None,
        "last_reset": _utcnow()
    })

    update_group_data(chat.id, group)


# =====================================================
# 2️⃣ DAILY GROUP ACTIVITY TRACK (ANTI SPAM SAFE)
# =====================================================
async def track_group_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return

    group = get_group_data(chat.id)
    now = _utcnow()

    if _need_reset(group.get("last_reset")):
        group["daily_msgs"] = 0
        group["reward_given"] = False
        group["reward_user"] = None
        group["last_reset"] = now

    group["daily_msgs"] = group.get("daily_msgs", 0) + 1

    if (
        group["daily_msgs"] >= DAILY_MSG_TARGET
        and not group["reward_given"]
    ):
        uid = update.effective_user.id

        group["wallet"] = group.get("wallet", 0) + DAILY_GROUP_REWARD
        group["reward_given"] = True
        group["reward_user"] = uid

        user = get_user_data(uid, update.effective_user)
        user["bal"] += DAILY_USER_REWARD
        update_user_data(uid, user)

        await update.message.reply_text(
            f"🎉 Daily Activity Completed!\n"
            f"🏦 Group +{DAILY_GROUP_REWARD}\n"
            f"👤 {update.effective_user.first_name} +{DAILY_USER_REWARD}"
        )

    update_group_data(chat.id, group)


# =====================================================
# 3️⃣ GROUP WALLET
# =====================================================
async def group_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return await update.message.reply_text("❌ Group only command.")

    group = get_group_data(chat.id)
    await update.message.reply_text(
        f"🏦 Group Wallet: {group.get('wallet', 0)} 💰"
    )


async def give_from_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        return

    member = await chat.get_member(user.id)
    if member.status not in ("administrator", "creator"):
        return await update.message.reply_text("❌ Admins only.")

    if len(context.args) != 2 or not update.message.entities:
        return await update.message.reply_text(
            "Usage: /givedp @user amount"
        )

    target = update.message.entities[1].user

    try:
        amount = int(context.args[1])
        if amount <= 0:
            raise ValueError
    except Exception:
        return await update.message.reply_text("❌ Invalid amount.")

    group = get_group_data(chat.id)
    if group.get("wallet", 0) < amount:
        return await update.message.reply_text(
            "❌ Insufficient group balance."
        )

    target_data = get_user_data(target.id, target)
    target_data["bal"] += amount
    group["wallet"] -= amount

    update_user_data(target.id, target_data)
    update_group_data(chat.id, group)

    await update.message.reply_text(
        f"✅ {amount} coins given to {target.first_name}"
    )


# =====================================================
# 4️⃣ /claim (ONE TIME PER GROUP)
# =====================================================
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        return await update.message.reply_text("❌ Group only.")

    if is_group_claimed(chat.id):
        return await update.message.reply_text(
            "❌ This group is already claimed."
        )

    try:
        members = await context.bot.get_chat_member_count(chat.id)
    except Exception:
        return await update.message.reply_text(
            "❌ Unable to fetch members."
        )

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
        return await update.message.reply_text(
            f"⏳ Try again after {str(timedelta(seconds=left)).split('.')[0]}"
        )

    users_col.update_one(
        {"id": user.id},
        {"$inc": {"bal": 1000}, "$set": {"last_daily": now}},
        upsert=True
    )

    await update.message.reply_text("✅ Daily reward: 1000 coins")


# =====================================================
# 🆕 6️⃣ DONATE TO GROUP
# =====================================================
async def donate_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ("group", "supergroup"):
        return

    if len(context.args) != 1:
        return await update.message.reply_text(
            "Usage: /donategroup amount"
        )

    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError
    except Exception:
        return await update.message.reply_text("❌ Invalid amount.")

    user_data = get_user_data(user.id, user)
    if user_data["bal"] < amount:
        return await update.message.reply_text("❌ Insufficient balance.")

    group = get_group_data(chat.id)

    user_data["bal"] -= amount
    group["wallet"] = group.get("wallet", 0) + amount

    update_user_data(user.id, user_data)
    update_group_data(chat.id, group)

    await update.message.reply_text(
        f"❤️ {user.first_name} donated {amount} coins to group!"
    )


# =====================================================
# 🆕 7️⃣ TOP GROUPS
# =====================================================
async def top_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    groups = list(context.application.bot_data.get("groups_cache", []))
    if not groups:
        return await update.message.reply_text("No data available.")

    groups = sorted(groups, key=lambda x: x.get("wallet", 0), reverse=True)[:10]

    text = "🏆 Top Groups\n\n"
    for i, g in enumerate(groups, 1):
        text += f"{i}. {g.get('title','Unknown')} — {g.get('wallet',0)} 💰\n"

    await update.message.reply_text(text)


# =====================================================
# REGISTER
# =====================================================
def register_game_commands(app):
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("groupbal", group_balance))
    app.add_handler(CommandHandler("givedp", give_from_group))
    app.add_handler(CommandHandler("donategroup", donate_group))
    app.add_handler(CommandHandler("topgroup", top_groups))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.GROUPS,
        track_group_activity
    ))
