# commands/couple.py

import os
import random
from datetime import datetime, timedelta
import pytz
from PIL import Image, ImageDraw

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# ====== PATHS ======
BG_PATH = "baka/assets/cppic.png"
DEFAULT_PIC = "baka/assets/upic.png"
TEMP1 = "baka/assets/pfp1.png"
TEMP2 = "baka/assets/pfp2.png"
OUT_IMG = "baka/assets/couple.png"

# ====== DATE UTILS ======
def get_today():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%d/%m/%Y")

def get_tomorrow():
    tz = pytz.timezone("Asia/Kolkata")
    return (datetime.now(tz) + timedelta(days=1)).strftime("%d/%m/%Y")

# ====== SIMPLE MEMORY DB (RESTART = RESET) ======
COUPLES = {}

# ====== MAIN COMMAND ======
async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "private":
        return await update.message.reply_text("❌ This command only works in groups.")

    today = get_today()
    tomorrow = get_tomorrow()

    key = f"{chat.id}_{today}"

    # ===== If already selected =====
    if key in COUPLES:
        c1_id, c2_id, img_path = COUPLES[key]

        try:
            u1 = await context.bot.get_chat(c1_id)
            u2 = await context.bot.get_chat(c2_id)
            n1 = u1.first_name
            n2 = u2.first_name
        except:
            return await update.message.reply_text("❌ Old couple data invalid. Try again.")

        txt = f"""
<b>Today's Couple of the Day 💖</b>

[{n1}](tg://user?id={c1_id}) + [{n2}](tg://user?id={c2_id}) = ❣️

Next couple will be selected on {tomorrow}!
"""

        return await update.message.reply_photo(
            photo=open(img_path, "rb"),
            caption=txt,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{context.bot.username}?startgroup=true")]
            ])
        )

    # ===== Pick members =====
    members = []
    async for m in context.bot.get_chat_administrators(chat.id):
        pass  # force permissions cache

    try:
        async for m in context.bot.get_chat_members(chat.id, limit=50):
            if not m.user.is_bot:
                members.append(m.user)
    except:
        return await update.message.reply_text("❌ I need admin permission to read members.")

    if len(members) < 2:
        return await update.message.reply_text("❌ Not enough members.")

    u1 = random.choice(members)
    u2 = random.choice(members)
    while u1.id == u2.id:
        u2 = random.choice(members)

    # ===== Download photos =====
    try:
        p1 = await context.bot.get_user_profile_photos(u1.id, limit=1)
        if p1.total_count > 0:
            f1 = await context.bot.get_file(p1.photos[0][-1].file_id)
            await f1.download_to_drive(TEMP1)
        else:
            TEMP1 = DEFAULT_PIC
    except:
        TEMP1 = DEFAULT_PIC

    try:
        p2 = await context.bot.get_user_profile_photos(u2.id, limit=1)
        if p2.total_count > 0:
            f2 = await context.bot.get_file(p2.photos[0][-1].file_id)
            await f2.download_to_drive(TEMP2)
        else:
            TEMP2 = DEFAULT_PIC
    except:
        TEMP2 = DEFAULT_PIC

    # ===== Image processing =====
    bg = Image.open(BG_PATH).convert("RGBA")
    img1 = Image.open(TEMP1).resize((437, 437)).convert("RGBA")
    img2 = Image.open(TEMP2).resize((437, 437)).convert("RGBA")

    def circle(im):
        mask = Image.new("L", im.size, 0)
        d = ImageDraw.Draw(mask)
        d.ellipse((0, 0, im.size[0], im.size[1]), fill=255)
        im.putalpha(mask)
        return im

    img1 = circle(img1)
    img2 = circle(img2)

    bg.paste(img1, (116, 160), img1)
    bg.paste(img2, (789, 160), img2)
    bg.save(OUT_IMG)

    # ===== Save =====
    COUPLES[key] = (u1.id, u2.id, OUT_IMG)

    txt = f"""
<b>Today's Couple of the Day 💖</b>

[{u1.first_name}](tg://user?id={u1.id}) + [{u2.first_name}](tg://user?id={u2.id}) = 💚

Next couple will be selected on {tomorrow}!
"""

    await update.message.reply_photo(
        photo=open(OUT_IMG, "rb"),
        caption=txt,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ])
    )
