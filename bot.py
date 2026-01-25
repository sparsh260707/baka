# bot.py
# Final BAKA Bot - Economy + AI Chatbot + Stickers + Emoji + Models + /start image

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
)
from dotenv import load_dotenv

# Load all keys from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Economy commands
from commands.economy import (
    bal, rob, kill, revive, protect,
    give, myrank, toprich, leaders, economy
)

# AI chatbot
from commands.chatbot import ask_ai, ai_message_handler

# Direct /start image
START_IMAGE_URL = "https://files.catbox.moe/yzpfuh.jpg"  # <-- change to your image URL

# ================== /START COMMAND ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [
            InlineKeyboardButton("💬 Talk to Baka", callback_data="talk_baka"),
            InlineKeyboardButton("✨ ⏤͟͞ 𝙎𝙋𝘼𝙍𝙎𝙃 𝘽𝘼𝙉𝙄𝙔𝘼", url="https://t.me/oye_sparsh")
        ],
        [
            InlineKeyboardButton("🧸 Friends", url="https://t.me/codebotnetwork"),
            InlineKeyboardButton("🎮 GAMES", url=f"https://t.me/{context.bot.username}")
        ],
        [
            InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{context.bot.username}?startgroup=true")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""✨ 𝗛𝗲𝘆, *{user.first_name}* ~
💌 You're Talking To 𝓑𝓪𝓴𝓪, A _Sassy Cutie Girl_ 💕

👇 Choose An Option Below:"""

    # If not private, ask user to check private
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "📩 Check your private chat to start!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Open Private", url=f"https://t.me/{context.bot.username}")]
            ])
        )
        await context.bot.send_message(
            chat_id=user.id,
            text=text,
            reply_markup=reply_markup
        )
    else:
        # Send image
        if START_IMAGE_URL.startswith("http"):
            await update.message.reply_photo(
                photo=START_IMAGE_URL, caption=text, reply_markup=reply_markup, parse_mode="Markdown"
            )
        else:
            with open(START_IMAGE_URL, "rb") as f:
                await update.message.reply_photo(
                    photo=InputFile(f), caption=text, reply_markup=reply_markup, parse_mode="Markdown"
                )

# ================== CALLBACK QUERY HANDLER ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "talk_baka":
        await query.message.reply_text(
            "Main thik hu, tum kaise ho? 😊\nYou can continue chatting with me here or type /ask <message>",
        )

# ================== MAIN BOT SETUP ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Start command
    app.add_handler(CommandHandler("start", start))

    # Callback buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    # Economy commands
    app.add_handler(CommandHandler("bal", bal))
    app.add_handler(CommandHandler("rob", rob))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("revive", revive))
    app.add_handler(CommandHandler("protect", protect))
    app.add_handler(CommandHandler("give", give))
    app.add_handler(CommandHandler("myrank", myrank))
    app.add_handler(CommandHandler("toprich", toprich))
    app.add_handler(CommandHandler("leaders", leaders))
    app.add_handler(CommandHandler("economy", economy))

    # AI chatbot
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_message_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
