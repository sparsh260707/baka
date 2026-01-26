# commands/kang.py
import os
import tempfile
from uuid import uuid4
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext

BOT_USERNAME = os.getenv("BOT_USERNAME")  # Your bot username without @

async def kang(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply = msg.reply_to_message

    if not reply:
        return await msg.reply_text("❌ Reply to a sticker, photo, or video to kang!")

    notify = await msg.reply_text("🔄 Processing... Please wait.")

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "file.png")
        is_animated = False
        is_video = False

        # Download media (PTB style)
        if reply.sticker:
            file = await reply.sticker.get_file()
            file_path = os.path.join(tmpdir, "sticker")
            await file.download_to_drive(file_path)
            is_animated = reply.sticker.is_animated
            is_video = reply.sticker.is_video

        elif reply.photo:
            file = await reply.photo[-1].get_file()
            file_path = os.path.join(tmpdir, "photo.png")
            await file.download_to_drive(file_path)

        elif reply.video or reply.animation:
            vid = reply.video or reply.animation
            file = await vid.get_file()
            file_path = os.path.join(tmpdir, "video.mp4")
            await file.download_to_drive(file_path)
            is_video = True
        else:
            return await notify.edit_text("❌ Unsupported media type!")

        # Resize image if static sticker/photo
        if not is_animated and not is_video:
            img = Image.open(file_path)
            img.thumbnail((512, 512))
            img.save(file_path, "PNG")

        # Generate pack short name
        user_id = msg.from_user.id
        short_name = f"cl_{uuid4().hex[:5]}_{user_id}_by_{BOT_USERNAME}"
        pack_title = f"{msg.from_user.first_name[:20]}'s Pack"
        emoji = reply.sticker.emoji if reply.sticker else "🤔"

        # Reply with download complete (PTB cannot create raw sticker packs directly)
        await notify.edit_text(
            f"✅ Kang complete!\n📦 File ready: {os.path.basename(file_path)}\n"
            f"Use a bot like @Stickers to manually add it to a pack.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📎 Open Stickers Bot", url="https://t.me/Stickers")]
            ])
        )

# PTB handler
kang_handler = CommandHandler("kang", kang)
