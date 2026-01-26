import os
import random
from datetime import datetime, timedelta

from PIL import Image, ImageDraw
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType

# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "baka", "assets")

BG_PATH = os.path.join(ASSETS_DIR, "cppic.png")
DEFAULT_USER_PATH = os.path.join(ASSETS_DIR, "upic.png")

# =========================
# SIMPLE DB CACHE
# =========================
_COUPLE_CACHE = {}

def get_couple(chat_id, date):
    return _COUPLE_CACHE.get(f"{chat_id}_{date}")

def save_couple(chat_id, date, data):
    _COUPLE_CACHE[f"{chat_id}_{date}"] = data

# =========================
# TIME HELPERS
# =========================
def today_date():
    return datetime.utcnow().strftime("%d/%m/%Y")

def tomorrow_date():
    return (datetime.utcnow() + timedelta(days=1)).strftime("%d/%m/%Y")

# =========================
# HELPER: get user's profile picture or fallback
# =========================
async def get_user_dp(user, save_path):
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos.total_count > 0:
            file = photos.photos[0][-1]
            f = await file.get_file()
            await f.download_to_drive(save_path)
            return save_path
        else:
            # User has no profile pic → use default UPIC
            return DEFAULT_USER_PATH
    except:
        return DEFAULT_USER_PATH

# =========================
# MAIN COMMAND
# =========================
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
        # Check DB cache
        data = get_couple(chat_id, today)

        if not data:
            msg = await message.reply_text("💞 Selecting today's couple...")

            # ------------------------
            # GET ALL NON-BOT MEMBERS
            # ------------------------
            members = []
            async for member in context.bot.get_chat_members(chat_id, limit=200):  # fetch first 200 members
                if not member.user.is_bot:
                    members.append(member.user.id)

            if len(members) < 2:
                return await msg.edit_text("❌ Not enough members to select a couple!")

            # Pick two random members
            c1_id = random.choice(members)
            c2_id = random.choice(members)
            while c1_id == c2_id:
                c2_id = random.choice(members)

            user1 = await context.bot.get_chat(c1_id)
            user2 = await context.bot.get_chat(c2_id)

            # ------------------------
            # GET PROFILE PHOTOS
            # ------------------------
            p1_path = await get_user_dp(user1, p1_path)
            p2_path = await get_user_dp(user2, p2_path)

            # ------------------------
            # IMAGE PROCESSING
            # ------------------------
            bg = Image.open(BG_PATH).convert("RGBA")
            img1 = Image.open(p1_path).convert("RGBA").resize((437, 437))
            img2 = Image.open(p2_path).convert("RGBA").resize((437, 437))

            # Circle mask
            mask = Image.new("L", img1.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, img1.size[0], img1.size[1]), fill=255)

            img1.putalpha(mask)
            img2.putalpha(mask)

            bg.paste(img1, (116, 160), img1)
            bg.paste(img2, (789, 160), img2)

            bg.save(out_path)

            # Save to cache
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
                if os.path.exists(f) and f not in [DEFAULT_USER_PATH, BG_PATH]:
                    os.remove(f)
            except:
                pass
