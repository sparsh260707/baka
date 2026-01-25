# commands/fun.py
import random
from telegram import Update
from telegram.ext import ContextTypes

# ==================== Helpers ====================

def mention(user):
    name = user.first_name.replace("<", "").replace(">", "")
    return f'<a href="tg://user?id={user.id}">{name}</a>'

def get_target(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None

# ==================== SLAP ====================

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    couple_videos = [
        "https://files.catbox.moe/ehwyr2.mp4",
        "https://files.catbox.moe/svkyzy.mp4"
    ]

    chat = update.effective_chat

    admins = await context.bot.get_chat_administrators(chat.id)

    members = [m.user for m in admins if not m.user.is_bot]

    if len(members) < 2:
        await update.message.reply_text("❌ Not enough users in group!")
        return

    u1, u2 = random.sample(members, 2)

    text = f"""
💖 <b>Today's Cute Couple</b> 💖

{mention(u1)} 💞 {mention(u2)}

Love is in the air 💘

~ From Shizu with love 💋
"""

    await update.message.reply_video(
        video=random.choice(couple_videos),
        caption=text,
        parse_mode="HTML"
    )
