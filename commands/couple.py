# commands/couple.py
import os
import random
from datetime import datetime, timedelta
import pytz
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from PIL import Image, ImageDraw
from telegraph import upload_file

from baka.utils import get_image, get_couple, save_couple
from baka import app

# ------------------- Helper Functions -------------------

def get_today_date():
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz)
    return now.strftime("%d/%m/%Y")

def get_tomorrow_date():
    tz = pytz.timezone("Asia/Kolkata")
    tomorrow = datetime.now(tz) + timedelta(days=1)
    return tomorrow.strftime("%d/%m/%Y")

# ------------------- Couple Command -------------------

@app.on_message(filters.command(["couple", "couples"]))
async def couple_of_the_day(_, message):
    chat_id = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("❌ This command only works in groups.")

    today = get_today_date()
    tomorrow = get_tomorrow_date()

    # ------------------- Paths -------------------
    p1_path = "baka/assets/pfp.png"        # temp user 1 pic
    p2_path = "baka/assets/pfp1.png"       # temp user 2 pic
    test_image_path = f"baka/assets/test_{chat_id}.png"  # final couple image
    cppic_path = "baka/assets/cppic.png"   # background image
    default_user_path = "baka/assets/upic.png"  # fallback profile pic

    try:
        selected = await get_couple(chat_id, today)

        if not selected:
            msg = await message.reply_text("❣️ Picking a couple...")

            # Get last 50 members
            users_list = []
            async for member in app.get_chat_members(chat_id, limit=50):
                if not member.user.is_bot and not member.user.is_deleted:
                    users_list.append(member.user.id)

            if len(users_list) < 2:
                return await msg.edit("❌ Not enough members to pick a couple.")

            # Randomly pick two
            c1_id = random.choice(users_list)
            c2_id = random.choice(users_list)
            while c1_id == c2_id:
                c2_id = random.choice(users_list)

            # Get profile photos
            photo1 = (await app.get_chat(c1_id)).photo
            photo2 = (await app.get_chat(c2_id)).photo

            N1 = (await app.get_users(c1_id)).mention
            N2 = (await app.get_users(c2_id)).mention

            # Download photos or use default
            try:
                p1 = await app.download_media(photo1.big_file_id, file_name=p1_path)
            except:
                p1 = default_user_path

            try:
                p2 = await app.download_media(photo2.big_file_id, file_name=p2_path)
            except:
                p2 = default_user_path

            # Open images and resize
            img1 = Image.open(p1).resize((437, 437))
            img2 = Image.open(p2).resize((437, 437))

            # Create circular masks
            mask1 = Image.new("L", img1.size, 0)
            draw = ImageDraw.Draw(mask1)
            draw.ellipse((0, 0) + img1.size, fill=255)
            img1.putalpha(mask1)

            mask2 = Image.new("L", img2.size, 0)
            draw = ImageDraw.Draw(mask2)
            draw.ellipse((0, 0) + img2.size, fill=255)
            img2.putalpha(mask2)

            # Open background
            img_bg = Image.open(cppic_path)
            img_bg.paste(img1, (116, 160), img1)
            img_bg.paste(img2, (789, 160), img2)
            img_bg.save(test_image_path)

            # Caption
            TXT = f"""
<b>Today's Couple of the Day:</b>

{N1} + {N2} = 💚

Next couples will be selected on {tomorrow}!!
"""
            await message.reply_photo(
                test_image_path,
                caption=TXT,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Add Me 🌋", url=f"https://t.me/{app.username}?startgroup=true")]]
                )
            )

            await msg.delete()

            # Upload to Telegraph
            uploaded = upload_file(test_image_path)
            img_url = "https://graph.org/" + uploaded[0]

            # Save couple data
            couple_data = {"c1_id": c1_id, "c2_id": c2_id}
            await save_couple(chat_id, today, couple_data, img_url)

        else:
            # Couple already selected
            msg = await message.reply_text("❣️")
            img_url = await get_image(chat_id)
            c1_id = int(selected["c1_id"])
            c2_id = int(selected["c2_id"])
            c1_name = (await app.get_users(c1_id)).first_name
            c2_name = (await app.get_users(c2_id)).first_name

            TXT = f"""
<b>Today's Couple of the Day 🎉:</b>

[{c1_name}](tg://openmessage?user_id={c1_id}) + [{c2_name}](tg://openmessage?user_id={c2_id}) = ❣️

Next couples will be selected on {tomorrow}!!
"""
            await message.reply_photo(
                img_url,
                caption=TXT,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Add Me 🌋", url=f"https://t.me/{app.username}?startgroup=true")]]
                )
            )
            await msg.delete()

    except Exception as e:
        print(f"Couple Error: {e}")

    finally:
        # Cleanup temporary user photos and generated couple image
        for f in [p1_path, p2_path, test_image_path]:
            try:
                os.remove(f)
            except:
                pass
