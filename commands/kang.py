# commands/kang.py
import os
import tempfile
import asyncio
from uuid import uuid4
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters

# Pyrogram for raw sticker pack operations
from pyrogram import Client
from pyrogram.raw import functions, types
from pyrogram.errors import StickersetInvalid

# ===== CONFIG =====
PYROGRAM_SESSION = "pyro_session"  # Path to Pyrogram session string/file
BOT_USERNAME = os.getenv("BOT_USERNAME")  # Telegram bot username without @

# ================= KANG HANDLER =================
async def kang(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply = msg.reply_to_message

    if not reply:
        return await msg.reply_text("❌ Reply to a sticker, photo, or video to kang!")

    notify = await msg.reply_text("🔄 Processing... Please wait.")

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "file")
        is_animated = False
        is_video = False

        # Download media
        if reply.sticker:
            file_path = await reply.sticker.get_file().download(custom_path=file_path)
            is_animated = reply.sticker.is_animated
            is_video = reply.sticker.is_video
        elif reply.photo:
            file_path = await reply.photo[-1].get_file().download(custom_path=file_path)
        elif reply.video or reply.animation:
            file_path = await (reply.video or reply.animation).get_file().download(custom_path=file_path)
            is_video = True
        else:
            return await notify.edit_text("❌ Unsupported media type!")

        # Resize image if static sticker
        if not is_animated and not is_video:
            img = Image.open(file_path)
            img.thumbnail((512, 512))
            img.save(file_path, "PNG")

        # Generate pack short name
        user_id = msg.from_user.id
        short_name = f"cl_{uuid4().hex[:5]}_{user_id}_by_{BOT_USERNAME}"

        pack_title = f"{msg.from_user.first_name[:20]}'s Pack"

        # Emoji for sticker
        emoji = "🤔"
        if reply.sticker:
            emoji = reply.sticker.emoji or "🤔"

        # ===== Use Pyrogram client to create pack =====
        async with Client(PYROGRAM_SESSION, bot_token=os.getenv("BOT_TOKEN")) as app:
            try:
                # Create new sticker pack
                await app.invoke(
                    functions.stickers.CreateStickerSet(
                        user_id=await app.resolve_peer(user_id),
                        title=pack_title,
                        short_name=short_name,
                        stickers=[
                            types.InputStickerSetItem(
                                document=types.InputDocument(
                                    id=(await app.upload_file(file_path)).id,
                                    access_hash=(await app.upload_file(file_path)).access_hash,
                                    file_reference=(await app.upload_file(file_path)).file_reference,
                                ),
                                emoji=emoji
                            )
                        ],
                        animated=is_animated,
                        videos=is_video
                    )
                )
                await notify.edit_text(
                    f"✅ Kanged successfully!\n📦 Pack: {pack_title}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📎 Open Pack", url=f"https://t.me/addstickers/{short_name}")]
                    ])
                )
            except StickersetInvalid:
                await notify.edit_text("❌ Could not create pack. Try again later.")
            except Exception as e:
                await notify.edit_text(f"❌ Error: {e}")

# ================== PTB HANDLER ==================
kang_handler = CommandHandler("kang", kang)
