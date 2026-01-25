import random
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_group_members
from PIL import Image, ImageDraw, ImageOps
import requests
from io import BytesIO

# Temporary storage for 24h logic
couple_cache = {}

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 24 Hour Check: Agar aaj ka couple pehle se bana hai
    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        c1 = couple_cache[chat_id]['c1']
        c2 = couple_cache[chat_id]['c2']
        return await update.message.reply_text(
            f"💌 Today's Couple is already chosen:\n\n👤 {c1['name']}\n❤️\n👤 {c2['name']}\n\nNext couple will be available tomorrow!"
        )

    msg = await update.message.reply_text("🔍 Searching for the perfect match...")

    # Group members fetch karna (MongoDB se)
    members = get_group_members(chat_id)
    
    if len(members) < 2:
        return await msg.edit_text("❌ Database mein kaafi members nahi mile. Sabko bolo group mein message karein!")

    # Randomly select two members
    c1, c2 = random.sample(members, 2)

    try:
        # Create Image (Pillow)
        bg = Image.new('RGB', (800, 400), color=(255, 182, 193)) # Pink BG
        
        async def get_pfp(user_id):
            try:
                photos = await context.bot.get_user_profile_photos(user_id, limit=1)
                if photos.total_count > 0:
                    file = await context.bot.get_file(photos.photos[0][-1].file_id)
                    response = requests.get(file.file_path)
                    img = Image.open(BytesIO(response.content)).convert("RGBA")
                    return img.resize((300, 300))
            except:
                return Image.new('RGBA', (300, 300), color="gray") # Default if no PFP

        img1 = await get_pfp(c1['id'])
        img2 = await get_pfp(c2['id'])

        # Paste images
        bg.paste(img1, (50, 50))
        bg.paste(img2, (450, 50))
        
        # Save & Send
        img_path = f"couple_{chat_id}.png"
        bg.save(img_path)

        caption = (
            f"✨ **Couple Of The Day** ✨\n\n"
            f"👤 [{c1['name']}](tg://user?id={c1['id']})\n"
            f"❤️\n"
            f"👤 [{c2['name']}](tg://user?id={c2['id']})\n\n"
            f"Congratulations! You both are today's match! 🎉"
        )

        await update.message.reply_photo(
            photo=open(img_path, 'rb'),
            caption=caption,
            parse_mode="Markdown"
        )
        
        # Cache update
        couple_cache[chat_id] = {'c1': c1, 'c2': c2, 'date': today}
        os.remove(img_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error generating couple: {e}")
