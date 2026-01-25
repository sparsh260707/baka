import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType

# Sahi imports
from utils import get_mention
from database.db import get_group_members

# Path Setup
ASSETS = Path("/root/assets")
BG_PATH = ASSETS / "cppic.png"
FALLBACK_PATH = ASSETS / "upic.png"

# Bot ki current directory ke hisaab se temp folder
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp_couples"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

couple_cache = {}

async def get_circular_avatar(bot, user_id):
    avatar_path = TEMP_DIR / f"avatar_{user_id}.png"
    size = (437, 437)

    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            await file.download_to_drive(avatar_path)
            img = Image.open(avatar_path).convert("RGBA")
            img.load() # Memory me load taaki file delete ho sake
        else:
            img = Image.open(FALLBACK_PATH).convert("RGBA")
    except Exception:
        img = Image.open(FALLBACK_PATH).convert("RGBA")

    # Pillow v10+ compatibility fix
    resampling = getattr(Image, 'Resampling', Image).LANCZOS
    img = img.resize(size, resampling)
    
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)

    output = ImageOps.fit(img, size, centering=(0.5, 0.5))
    output.putalpha(mask)

    if avatar_path.exists():
        try:
            os.remove(avatar_path)
        except:
            pass

    return output

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

    today = datetime.now().strftime("%d/%m/%Y")
    chat_id = chat.id

    # Cache Check with proper file opening
    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        data = couple_cache[chat_id]
        if os.path.exists(data['img_path']):
            with open(data['img_path'], 'rb') as photo:
                return await update.message.reply_photo(
                    photo=photo, caption=data['caption'], parse_mode=ParseMode.HTML
                )

    # Background Path validation
    bg_to_use = BG_PATH if BG_PATH.exists() else FALLBACK_PATH
    
    if not bg_to_use.exists():
        return await update.message.reply_text(f"❌ Error: Required assets not found in {ASSETS}")

    msg = await update.message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ...")

    members = get_group_members(chat_id)
    if not members or len(members) < 2:
        await msg.delete()
        return await update.message.reply_text("⚠️ Not enough active members found.")

    try:
        base = Image.open(bg_to_use).convert("RGBA")
        
        c1_db, c2_db = random.sample(members, 2)
        p1_img = await get_circular_avatar(context.bot, c1_db["id"])
        p2_img = await get_circular_avatar(context.bot, c2_db["id"])

        # Pasting avatars
        base.paste(p1_img, (116, 160), p1_img)
        base.paste(p2_img, (789, 160), p2_img)

        final_img_path = TEMP_DIR / f"couple_{chat_id}.png"
        base.save(final_img_path)

        m1 = get_mention(c1_db)
        m2 = get_mention(c2_db)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')

        caption = (
            f"<b>ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :</b>\n\n"
            f"💞 {m1} + {m2} = ❤️\n\n"
            f"<b>ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!</b>"
        )

        couple_cache[chat_id] = {
            "date": today, "img_path": str(final_img_path), "caption": caption
        }

        with open(final_img_path, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode=ParseMode.HTML)
        
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Image generation failed: {str(e)}")
