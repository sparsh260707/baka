# commands/couple.py
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType, ParseMode

from baka.utils import get_mention, get_couple, save_couple
from database.db import get_group_members

# =========================
# PATHS
# =========================
ASSETS_DIR = Path("baka/assets")
BG_PATH = ASSETS_DIR / "cppic.png"
DEFAULT_USER_PATH = ASSETS_DIR / "upic.png"
TEMP_DIR = Path("temp_couples")

TEMP_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# DATE HELPERS
# =========================
def today_date():
    return datetime.utcnow().strftime("%d/%m/%Y")

def tomorrow_date():
    return (datetime.utcnow() + timedelta(days=1)).strftime("%d/%m/%Y")


# =========================
# GET USER DP
# =========================
async def get_user_dp(user_id, bot, save_path):
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            await file.download_to_drive(save_path)
            img = Image.open(save_path).convert("RGBA")
        else:
            img = Image.open(DEFAULT_USER_PATH).convert("RGBA")
    except:
        img = Image.open(DEFAULT_USER_PATH).convert("RGBA")

    # Circular mask
    size = (437, 437)
    img = img.resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(img, size, centering=(0.5, 0.5))
    output.putalpha(mask)

    # Cleanup temp file
    if save_path.exists():
        os.remove(save_path)
    return output


# =========================
# MAIN COMMAND
# =========================
async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message

    if chat.type == ChatType.PRIVATE:
        return await message.reply_text("❌ This command only works in groups!")

    chat_id = chat.id
    today = today_date()
    tomorrow = tomorrow_date()

    # Check DB cache
    data = await get_couple(chat_id, today)
    if data:
        u1 = await context.bot.get_chat(data["c1_id"])
        u2 = await context.bot.get_chat(data["c2_id"])
        caption = f"""
💖 <b>Today's Couple of the Day</b>

{u1.mention_html()} + {u2.mention_html()} = 💞

⏭ Next couple will be selected on <b>{tomorrow}</b>
"""
        return await message.reply_photo(data["image"], caption=caption, parse_mode=ParseMode.HTML)

    msg = await message.reply_text("💞 Selecting today's couple...")

    # Fetch group members from DB
    members = get_group_members(chat_id)
    members = [m for m in members if not m.get("is_bot")]  # filter bots

    if len(members) < 2:
        await msg.delete()
        return await message.reply_text("❌ Not enough members to select a couple!")

    # Pick two random users
    c1, c2 = random.sample(members, 2)
    c1_id = c1["id"]
    c2_id = c2["id"]

    # Prepare temp paths
    p1_path = TEMP_DIR / f"p1_{chat_id}.png"
    p2_path = TEMP_DIR / f"p2_{chat_id}.png"
    out_path = TEMP_DIR / f"couple_{chat_id}.png"

    # Download avatars and process
    p1_img = await get_user_dp(c1_id, context.bot, p1_path)
    p2_img = await get_user_dp(c2_id, context.bot, p2_path)

    # Create final image
    bg = Image.open(BG_PATH).convert("RGBA")
    bg.paste(p1_img, (116, 160), p1_img)
    bg.paste(p2_img, (789, 160), p2_img)
    bg.save(out_path)

    # Save to DB
    await save_couple(chat_id, today, {"c1_id": c1_id, "c2_id": c2_id}, str(out_path))

    # Prepare caption
    caption = f"""
💖 <b>Today's Couple of the Day</b>

{get_mention(c1)} + {get_mention(c2)} = 💞

⏭ Next couple will be selected on <b>{tomorrow}</b>
"""

    await message.reply_photo(
        str(out_path),
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{context.bot.username}?startgroup=true")]
        ])
    )

    await msg.delete()
