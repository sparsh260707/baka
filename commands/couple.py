import random
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_group_members
from PIL import Image, ImageDraw, ImageOps
import requests
from io import BytesIO

# 24h Couple Storage
couple_cache = {}

async def get_pfp(bot, user_id):
    """User ki profile photo download karke PIL image return karta hai."""
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            response = requests.get(file.file_path)
            img = Image.open(BytesIO(response.content)).convert("RGBA")
            return img.resize((300, 300))
    except:
        pass
    return Image.new('RGBA', (300, 300), color=(200, 200, 200)) # Default Gray

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private":
        return await update.message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

    chat_id = chat.id
    today = datetime.now().strftime("%Y-%m-%d")

    # 24 Hour Logic: Check if couple already exists for today
    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        data = couple_cache[chat_id]
        return await update.message.reply_photo(
            photo=open(data['path'], 'rb'),
            caption=f"💌 **Today's Couple of the Day:**\n\n👤 {data['c1_name']} + {data['c2_name']} = ❤️"
        )

    msg = await update.message.reply_text("🔍 Choosing today's lucky couple...")

    # MongoDB se group members (seen_groups logic) fetch karna
    members = get_group_members(chat_id)
    members = [m for m in members if m and 'id' in m]

    if len(members) < 2:
        return await msg.edit_text("⚠️ Not enough active members found in database.")

    # Random Selection
    c1, c2 = random.sample(members, 2)

    try:
        # Create Couple Image
        canvas = Image.new('RGB', (800, 400), color=(255, 192, 203)) # Pink Canvas
        
        pfp1 = await get_pfp(context.bot, c1['id'])
        pfp2 = await get_pfp(context.bot, c2['id'])

        canvas.paste(pfp1, (50, 50))
        canvas.paste(pfp2, (450, 50))
        
        # Draw Heart in middle
        draw = ImageDraw.Draw(canvas)
        # Simple Heart or Text
        draw.text((385, 180), "❤️", fill=(255, 0, 0))

        img_path = f"temp_couple_{chat_id}.png"
        canvas.save(img_path)

        caption = (
            f"✨ **ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ** ✨\n\n"
            f"💞 [{c1['name']}](tg://user?id={c1['id']}) + "
            f"[{c2['name']}](tg://user?id={c2['id']}) = ❤️\n\n"
            f"ᴛʜᴇsᴇ ᴛᴡᴏ ᴀʀᴇ ᴛᴏᴅᴀʏ's ᴍᴀᴛᴄʜ! ɴᴇxᴛ ᴄᴏᴜᴘʟᴇ ɪɴ 24 ʜᴏᴜʀs."
        )

        await update.message.reply_photo(
            photo=open(img_path, 'rb'),
            caption=caption,
            parse_mode="Markdown"
        )

        # Store in cache for 24h
        couple_cache[chat_id] = {
            'date': today, 
            'path': img_path,
            'c1_name': c1['name'],
            'c2_name': c2['name']
        }
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")
