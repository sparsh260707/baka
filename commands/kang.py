# commands/kang.py
import os
import asyncio
from pathlib import Path
from PIL import Image
from telegram import Update, InputFile
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

from utils.files import resize_file_to_sticker_size, save_temp_file, cleanup_temp_file

TEMP_DIR = Path("temp_stickers")
TEMP_DIR.mkdir(exist_ok=True)

async def kang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    reply = message.reply_to_message
    if not reply:
        return await message.reply_text("📎 Reply to an image/sticker to kang it!")

    # Determine file type
    file = None
    if reply.sticker:
        file = await reply.sticker.get_file()
    elif reply.photo:
        file = await reply.photo[-1].get_file()
    elif reply.document and (reply.document.mime_type.startswith("image/") or reply.document.mime_type.endswith("gif")):
        file = await reply.document.get_file()
    else:
        return await message.reply_text("❌ Unsupported media type!")

    msg = await message.reply_text("🔄 Processing...")

    # Download file to temp
    temp_path = TEMP_DIR / f"{file.file_id}"
    await file.download_to_drive(str(temp_path))

    # Resize if image
    if not reply.sticker.is_animated if reply.sticker else True:
        temp_path = Path(await resize_file_to_sticker_size(str(temp_path)))

    # Send as sticker
    try:
        if reply.sticker and reply.sticker.is_animated:
            await message.reply_document(document=str(temp_path), caption="✅ Animated sticker (TGS)")
        else:
            await message.reply_sticker(sticker=InputFile(str(temp_path)))
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

    # Cleanup temp
    await cleanup_temp_file(str(temp_path))
    await msg.delete()


kang_handler = CommandHandler(["kang"], kang)
