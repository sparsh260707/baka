import os
import random
from datetime import datetime, timedelta

from PIL import Image, ImageDraw
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType

from database.db import get_couple, save_couple

# ===== Paths =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

BG_PATH = os.path.join(ASSETS_DIR, "cppic.png")
DEFAULT_USER_PATH = os.path.join(ASSETS_DIR, "upic.png")

# ===== Time (India) =====
def today_date():
    return datetime.utcnow().strftime("%d/%m/%Y")

def tomorrow_date():
    return (datetime.utcnow() + timedelta(days=1)).strftime("%d/%m/%Y")

# ===== Main Command =====
async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == ChatType.PRIVATE:
        return await message.reply_text("❌ This command only works in groups!")

    chat_id = chat.id
    today = today_date()
    tomorrow = tomorrow_date()

    # Temp files
    p1_path = os.path.join(ASSETS_DIR, f"p1_{chat_id}.png")
    p2_path = os.path.join(ASSETS_DIR, f"p2_{chat_id}.png")
    out_path = os.path.join(ASSETS_DIR, f"couple_{chat_id}.png")

    try:
        # Check DB
        data = get_couple(chat_id, today)

        if not data:
            msg = await message.reply_text("💞 Selecting today's couple...")

            members = []

            admins = await context.bot.get_chat_administrators(chat_id)
            for m in admins:
                if not m.user.is_bot:
                    members.append(m.user.id)

            if len(members) < 2:
                return await msg.edit_text("❌ Not enough members!")

            c1_id = random.choice(members)
            c2_id = random.choice(members)
            while c1_id == c2_id:
                c2_id = random.choice(members)

            user1 = await context.bot.get_chat(c1_id)
            user2 = await context.bot.get_chat(c2_id)

            # Download photos or use default
            try:
                p1_file = await user1.get_profile_photos(limit=1)
                if p1_file.total_count > 0:
                    file = p1_file.photos[0][-1]
                    f = await file.get_file()
                    await f.download_to_drive(p1_path)
                else:
                    raise Exception()
            except:
                p1_path = DEFAULT_USER_PATH

            try:
                p2_file = await user2.get_profile_photos(limit=1)
                if p2_file.total_count > 0:
                    file = p2_file.photos[0][-1]
                    f = await file.get_file()
                    await f.download_to_drive(p2_path)
                else:
                    raise Exception()
            except:
                p2_path = DEFAULT_USER_PATH

            # ===== Image processing =====
            bg = Image.open(BG_PATH).convert("RGBA")
            img1 = Image.open(p1_path).convert("RGBA").resize((437, 437))
            img2 = Image.open(p2_path).convert("RGBA").resize((437, 437))

            # Circle mask
            mask = Image.new("L", img1.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + img1.size, fill=255)

            img1.putalpha(mask)
            img2.putalpha(mask)

            bg.paste(img1, (116, 160), img1)
            bg.paste(img2, (789, 160), img2)

            bg.save(out_path)

            # Save to DB
            save_couple(chat_id, today, {
                "c1_id": c1_id,
                "c2_id": c2_id,
                "image": out_path
            })

            caption = f"""
💖 <b>Today's Couple of the Day</b>

{user1.mention_html()} + {user2.mention_html()} = 💞

⏭ Next couple will be selected on <b>{tomorrow}</b>
"""

            await message.reply_photo(
                out_path,
                caption=caption,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{context.bot.username}?startgroup=true")]
                ])
            )

            await msg.delete()

        else:
            c1_id = int(data["c1_id"])
            c2_id = int(data["c2_id"])
            img = data["image"]

            u1 = await context.bot.get_chat(c1_id)
            u2 = await context.bot.get_chat(c2_id)

            caption = f"""
💖 <b>Today's Couple of the Day</b>

{u1.mention_html()} + {u2.mention_html()} = 💞

⏭ Next couple will be selected on <b>{tomorrow}</b>
"""

            await message.reply_photo(
                img,
                caption=caption,
                parse_mode="HTML"
            )

    except Exception as e:
        print("COUPLE ERROR:", e)
        await message.reply_text("❌ Something went wrong while making couple 😢")

    finally:
        # Cleanup temp files
        for f in [p1_path, p2_path]:
            try:
                if os.path.exists(f) and "upic.png" not in f:
                    os.remove(f)
            except:
                pass
