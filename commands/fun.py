# commands/fun.py
import random
from telegram import Update
from telegram.ext import ContextTypes
from database.db import load, save

# ==================== Helpers ====================

def mention(user):
    name = user.first_name.replace("<", "").replace(">", "")
    return f'<a href="tg://user?id={user.id}">{name}</a>'

def get_target(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None

# Track users in group (for /couple)
def track_user(update: Update):
    if not update.effective_chat or not update.effective_user:
        return

    chat_id = str(update.effective_chat.id)
    user = update.effective_user

    data = load()

    if chat_id not in data:
        data[chat_id] = {}

    if str(user.id) not in data[chat_id]:
        data[chat_id][str(user.id)] = {
            "name": user.first_name,
            "coins": 0
        }
        save(data)

# ==================== SLAP ====================

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)

    videos = [
        "https://files.catbox.moe/ncuiok.mp4",
        "https://files.catbox.moe/9yo533.mp4",
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        await update.message.reply_text("❗ Kisi ke message pe reply karke /slap likho")
        return

    text = f"{mention(sender)} slapped {mention(target)} 👋"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== HUG ====================

async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)

    videos = [
        "https://files.catbox.moe/ehwyr2.mp4",
        "https://files.catbox.moe/svkyzy.mp4"
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        await update.message.reply_text("❗ Kisi ke message pe reply karke /hug likho")
        return

    text = f"{mention(sender)} sent a hug to {mention(target)} 🤗"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== PUNCH ====================

async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)

    videos = [
        "https://files.catbox.moe/yzqsz6.mp4",
        "https://files.catbox.moe/6gpa4z.mp4"
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        await update.message.reply_text("❗ Kisi ke message pe reply karke /punch likho")
        return

    text = f"{mention(sender)} punched {mention(target)} really hard 👊"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== KISS ====================

async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)

    videos = [
        "https://files.catbox.moe/ehi5uo.mp4",
        "https://files.catbox.moe/bwscnj.mp4"
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        await update.message.reply_text("❗ Kisi ke message pe reply karke /kiss likho")
        return

    text = f"{mention(sender)} gave a sweet kiss to {mention(target)} 😘💋"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== COUPLE ====================

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)

    couple_videos = [
        "https://files.catbox.moe/ehwyr2.mp4",
        "https://files.catbox.moe/svkyzy.mp4"
    ]

    data = load()
    chat_id = str(update.effective_chat.id)

    if chat_id not in data or len(data[chat_id]) < 2:
        await update.message.reply_text("❌ Not enough active users in this group!")
        return

    users = list(data[chat_id].keys())

    u1_id, u2_id = random.sample(users, 2)

    try:
        u1 = await context.bot.get_chat(int(chat_id), int(u1_id))
        u2 = await context.bot.get_chat(int(chat_id), int(u2_id))
    except:
        await update.message.reply_text("❌ Try again!")
        return

    text = f"""
💖 <b>Today's Cute Couple</b> 💖

<a href="tg://user?id={u1_id}">{u1.first_name}</a> 💞 <a href="tg://user?id={u2_id}">{u2.first_name}</a>

Love is in the air 💘

~ From Shizu with love 💋
"""

    await update.message.reply_video(
        video=random.choice(couple_videos),
        caption=text,
        parse_mode="HTML"
    )
