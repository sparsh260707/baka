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

# ==================== /slap ====================
async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = [
        "https://files.catbox.moe/ncuiok.mp4",
        "https://files.catbox.moe/9yo533.mp4",
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        return await update.message.reply_text("❗ Kisi ke message pe reply karke /slap likho")

    text = f"{mention(sender)} slapped {mention(target)} 👋"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== /hug ====================
async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = [
        "https://files.catbox.moe/ehwyr2.mp4",
        "https://files.catbox.moe/svkyzy.mp4"
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        return await update.message.reply_text("❗ Kisi ke message pe reply karke /hug likho")

    text = f"{mention(sender)} sent a hug to {mention(target)} 🤗"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== LOVE ====================
async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    target = get_target(update)

    if not target:
        return await update.message.reply_text("Reply to someone !")

    percent = random.randint(10, 100)

    text = f"""
💕 <b>Love meter report</b> 💕
{mention(sender)} ❤️ {mention(target)}
<b>Love compatibility:</b> {percent}% 🔥
"""

    await update.message.reply_text(text, parse_mode="HTML")

# ==================== STUPID METER ====================
async def stupid_meter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = get_target(update)

    if not target:
        return await update.message.reply_text("Reply to someone !")

    percent = random.randint(1, 100)

    text = f"""
Hmm 🤔 Stupid meter scanning...
<b>Result for</b> {mention(target)}: {percent}% 😵‍💫 stupid detected
"""

    await update.message.reply_text(text, parse_mode="HTML")

# ==================== /punch ====================
async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = [
        "https://files.catbox.moe/yzqsz6.mp4",
        "https://files.catbox.moe/6gpa4z.mp4"
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        return await update.message.reply_text("❗ Kisi ke message pe reply karke /punch likho")

    text = f"{mention(sender)} punched {mention(target)} really hard 👊"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== /kiss ====================
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = [
        "https://files.catbox.moe/ehi5uo.mp4",
        "https://files.catbox.moe/bwscnj.mp4"
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        return await update.message.reply_text("❗ Kisi ke message pe reply karke /kiss likho")

    text = f"{mention(sender)} gave a sweet kiss to {mention(target)} 😘💋"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== /bite ====================
async def bite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = [
        "https://files.catbox.moe/q91bhd.mp4",
        "https://files.catbox.moe/q91bhd.mp4",
    ]

    sender = update.effective_user
    target = get_target(update)

    if not target:
        return await update.message.reply_text("❗ Kisi ke message pe reply karke /bite likho")

    text = f"😈 {mention(sender)} gave a naughty bite to {mention(target)} 😁"

    await update.message.reply_video(
        video=random.choice(videos),
        caption=text,
        parse_mode="HTML"
    )

# ==================== /crush ====================
async def crush(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = get_target(update)
    if not target:
        return await update.message.reply_text("Reply to someone to check their crush 😁")

    user = update.effective_user
    percent = random.randint(40, 100)

    text = (
        f"💘 {mention(user)} ka secret crush hai {mention(target)}\n"
        f"❤️ Crush level: {percent}%"
    )

    await update.message.reply_text(text, parse_mode="HTML")

# ==================== /brain ====================
async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = get_target(update)
    if not target:
        return await update.message.reply_text("Reply to someone !🤖")

    iq = random.randint(50, 160)
    text = f"🧠 IQ level of {mention(target)} is {iq}% 😎"

    await update.message.reply_text(text, parse_mode="HTML")

# ==================== /id ====================
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    text = (
        f"👤 Your User ID: {user.id}\n"
        f"👥 Group ID: {chat.id}"
    )

    await update.message.reply_text(text)
