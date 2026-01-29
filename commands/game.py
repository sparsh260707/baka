import time
from datetime import datetime, timedelta

from telegram import Update, ChatMember
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# Yahan humne aapke db.py ke hisab se names fix kar diye hain
from database.db import (
    get_user,           # 'get_user_data' ki jagah 'get_user'
    users_col,
    get_group_data,
    update_group_data,
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

# INTERNAL HELPERS
def _utcnow():
    return datetime.utcnow()

def _need_reset(last_reset: datetime):
    if not last_reset:
        return True
    return (_utcnow() - last_reset) >= timedelta(hours=DAILY_RESET_HOURS)

# Helper to update user balance since update_user_data wasn't in your db.py
def _update_user_bal(user_id, amount):
    users_col.update_one(
        {"id": int(user_id)},
        {"$inc": {"bal": amount}},
        upsert=True
    )

# 1️⃣ BOT ADDED → GROUP JOIN BONUS
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
        # get_user returns the dict, we then update balance
        _update_user_bal(owner.id, OWNER_JOIN_BONUS)

    group.update({
        "wallet": group.get("wallet", 0) + 500,
        "joined_bonus_given": True,
        "daily_msgs": 0,
        "reward_given": False,
        "last_reset": _utcnow()
    })
    update_group_data(chat.id, group)

# 2️⃣ DAILY GROUP ACTIVITY TRACK
async def track_group_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return

    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return

    group = get_group_data(chat.id)
    now = _utcnow()

    if _need_reset(group.get("last_reset")):
        group["daily_msgs"] = 0
        group["reward_given"] = False
        group["last_reset"] = now

    group["daily_msgs"] = group.get("daily_msgs", 0) + 1

    if group["daily_msgs"] >= DAILY_MSG_TARGET and not group.get("reward_given"):
        uid = update.effective_user.id
        group["wallet"] = group.get("wallet", 0) + DAILY_GROUP_REWARD
        group["reward_given"] = True
        
        _update_user_bal(uid, DAILY_USER_REWARD)

        await update.message.reply_text(
            f"🎉 Daily Activity Completed!\n"
            f"🏦 Group +{DAILY_GROUP_REWARD}\n"
            f"👤 {update.effective_user.first_name} +{DAILY_USER_REWARD}"
        )

    update_group_data(chat.id, group)

# 3️⃣ GROUP WALLET & GIVE
async def group_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ("group", "supergroup"):
        return await update.message.reply_text("❌ Group only command.")

    group = get_group_data(chat.id)
    await update.message.reply_text(f"🏦 Group Wallet: {group.get('wallet', 0)} 💰")

async def give_from_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"): return

    member = await chat.get_member(user.id)
    if member.status not in ("administrator", "creator"):
        return await update.message.reply_text("❌ Admins only.")

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /givedp @user amount")

    # Handle Reply or Mention
    target_user = None
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    elif update.message.entities:
        for entity in update.message.entities:
            if entity.type == "text_mention": target_user = entity.user
    
    if not target_user:
        return await update.message.reply_text("❌ Please reply to a user or mention them.")

    try:
        amount = int(context.args[-1]) # Last arg is usually amount
        if amount <= 0: raise ValueError
    except:
        return await update.message.reply_text("❌ Invalid amount.")

    group = get_group_data(chat.id)
    if group.get("wallet", 0) < amount:
        return await update.message.reply_text("❌ Insufficient group balance.")

    group["wallet"] -= amount
    _update_user_bal(target_user.id, amount)
    update_group_data(chat.id, group)

    await update.message.reply_text(f"✅ {amount} coins given to {target_user.first_name}")

# 4️⃣ /claim
async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"): return

    if is_group_claimed(chat.id):
        return await update.message.reply_text("❌ This group is already claimed.")

    members = await context.bot.get_chat_member_count(chat.id)
    if members < 100:
        return await update.message.reply_text("❌ Minimum 100 members required.")

    reward = members * 3
    get_user(user, chat.id) # Ensure user exists
    _update_user_bal(user.id, reward)
    mark_group_claimed(chat.id, user.id)

    await update.message.reply_text(f"✅ Group Claimed!\n👥 Members: {members}\n💰 Reward: {reward}")

# 5️⃣ /daily (DM ONLY)
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return await update.message.reply_text("⚠️ Use this command in DM only.")

    user = update.effective_user
    data = get_user(user)
    now = int(time.time())
    last = data.get("last_daily", 0)

    if now - last < 86400:
        left = 86400 - (now - last)
        return await update.message.reply_text(f"⏳ Try again after {str(timedelta(seconds=left)).split('.')[0]}")

    users_col.update_one({"id": user.id}, {"$inc": {"bal": 1000}, "$set": {"last_daily": now}})
    await update.message.reply_text("✅ Daily reward: 1000 coins")

# 6️⃣ DONATE TO GROUP
async def donate_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type not in ("group", "supergroup"): return

    try:
        amount = int(context.args[0])
        if amount <= 0: raise ValueError
    except:
        return await update.message.reply_text("Usage: /donategroup amount")

    user_data = get_user(user)
    if user_data.get("bal", 0) < amount:
        return await update.message.reply_text("❌ Insufficient balance.")

    group = get_group_data(chat.id)
    _update_user_bal(user.id, -amount)
    group["wallet"] = group.get("wallet", 0) + amount
    update_group_data(chat.id, group)

    await update.message.reply_text(f"❤️ {user.first_name} donated {amount} coins to group!")

# 7️⃣ TOP GROUPS
async def top_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fetching from DB directly since cache might be empty
    from database.db import groups_col
    top_list = list(groups_col.find().sort("wallet", -1).limit(10))
    
    if not top_list:
        return await update.message.reply_text("No data available.")

    text = "🏆 **Top Groups by Wallet**\n\n"
    for i, g in enumerate(top_list, 1):
        text += f"{i}. Group ID: `{g.get('chat_id')}` — {g.get('wallet',0)} 💰\n"

    await update.message.reply_text(text)

# REGISTER
def register_game_commands(app):
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("groupbal", group_balance))
    app.add_handler(CommandHandler("givedp", give_from_group))
    app.add_handler(CommandHandler("donategroup", donate_group))
    app.add_handler(CommandHandler("topgroup", top_groups))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, track_group_activity))
