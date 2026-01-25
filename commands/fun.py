# commands/fun.py
import random
from telegram import Update
from telegram.ext import ContextTypes
from database.db import load, save

# ==================== Helpers ====================

def mention_id(uid, name):
    name = name.replace("<", "").replace(">", "")
    return f'<a href="tg://user?id={uid}">{name}</a>'

def mention(user):
    return mention_id(user.id, user.first_name)

def get_target(update: Update):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    return None

# ==================== Track Users ====================
def track_user(update: Update, user=None):
    if not update.effective_chat:
        return

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    chat_id = str(update.effective_chat.id)
    if user is None:
        user = update.effective_user

    data = load()

    if chat_id not in data:
        data[chat_id] = {}

    if str(user.id) not in data[chat_id]:
        data[chat_id][str(user.id)] = {"name": user.first_name}
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
    chat = update.effective_chat

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("❌ This command only works in groups!")
        return

    # 1. Fetch all members from Telegram
    try:
        all_members = []
        async for member in context.bot.get_chat_administrators(chat.id):
            if not member.user.is_bot:
                all_members.append(member.user)
        # If there are normal members, add them as well
        chat_members = await context.bot.get_chat(chat.id)
    except:
        await update.message.reply_text("❌ Failed to fetch members. Try again later.")
        return

    # 2. Ensure at least 2 human members
    humans = [m for m in all_members if not m.is_bot]
    if len(humans) < 2:
        await update.message.reply_text("❌ Not enough human members to make a couple!")
        return

    # 3. Pick 2 random humans
    u1, u2 = random.sample(humans, 2)

    # 4. Track them in database
    track_user(update, u1)
    track_user(update, u2)

    # 5. Prepare caption
    text = f"""
💖 <b>Today's Cute Couple</b> 💖

{mention(u1)} 💞 {mention(u2)}

Love is in the air 💘

~ From Shizu with love 💋
"""

    # 6. Send video
    couple_videos = [
        "https://files.catbox.moe/ehwyr2.mp4",
        "https://files.catbox.moe/svkyzy.mp4"
    ]
    await update.message.reply_video(
        video=random.choice(couple_videos),
        caption=text,
        parse_mode="HTML"
    )
