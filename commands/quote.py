# commands/quote.py
import httpx
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes

API_URL = "https://bot.lyo.su/quote/generate.png"

async def q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❗ Kisi message ko reply karke /q likho")

    msg = update.message.reply_to_message
    user = msg.from_user

    text = msg.text or msg.caption
    if not text:
        return await update.message.reply_text("❌ Is message ko quote nahi bana sakta")

    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [
            {
                "chatId": user.id,
                "text": text,
                "avatar": True,
                "from": {
                    "id": user.id,
                    "name": user.first_name,
                    "username": user.username or "",
                    "type": "private",
                    "photo": ""
                }
            }
        ]
    }

    wait = await update.message.reply_text("🖼️ Quote bana raha hoon...")

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(API_URL, json=payload)

        if r.status_code != 200:
            await wait.delete()
            return await update.message.reply_text("❌ Quote generate nahi ho paya")

        img = BytesIO(r.content)
        img.name = "quote.png"

        await wait.delete()
        await update.message.reply_photo(photo=img)

    except Exception as e:
        await wait.delete()
        await update.message.reply_text(f"❌ Error: {e}")
