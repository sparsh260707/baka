# bot.py
# Final BAKA Bot - Economy + AI Chatbot + Fun + Games + Admin + Auto-Registration

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
)
from dotenv import load_dotenv

# ================== LOAD ENV ==================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ================== IMPORT DATABASE LOGIC ==================
from database.db import get_user  # Har message pe register karne ke liye

# ================== IMPORT COMMANDS ==================
# Economy commands
from commands.economy import (
    bal, rob, kill, revive, protect,
    give, myrank, toprich, leaders, economy
)

# Game commands
from commands.game import register_game_commands

# Admin commands
from commands.admin import register_admin_commands

# AI chatbot
from commands.chatbot import ask_ai, ai_message_handler

# Fun commands
from commands.fun import slap, hug, punch, kiss
from commands.couple import couple 

# ================== START IMAGE ==================
START_IMAGE_URL = "https://files.catbox.moe/yzpfuh.jpg"

# ================== AUTO-REGISTER HANDLER ==================
async def auto_register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har message par user aur group ko register karta hai."""
    if not update.effective_user or update.effective_user.is_bot:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Database mein user aur group ID save karein
    get_user(user, chat_id)

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

    # Private chat logic
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "📩 Check your private chat to start!",
            reply_markup=InlineKeyboardMarkup([[ 
                InlineKeyboardButton("💬 Open Private", url=f"https://t.me/{context.bot.username}")
            ]])
        )
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except:
            pass
        return

    # Send image in private
    if START_IMAGE_URL.startswith("http"):
        await update.message.reply_photo(
            photo=START_IMAGE_URL,
            caption=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        with open(START_IMAGE_URL, "rb") as f:
            await update.message.reply_photo(
                photo=InputFile(f),
                caption=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

# ================== CALLBACK QUERY HANDLER ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "talk_baka":
        await query.message.reply_text(
            "Main thik hu, tum kaise ho? 😊\nYou can continue chatting with me here or type /ask <message>"
        )

# ================== ERROR HANDLER ==================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"❌ Error: {context.error}")
    if hasattr(update, "message") and update.message:
        await update.message.reply_text("⚠️ Something went wrong, try again!")

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ================= AUTO-REGISTRATION (Highest Priority) =================
    # Ye handler har text/command message par trigger hoga
    app.add_handler(MessageHandler(filters.ALL, auto_register_handler), group=-1)

    # ================= BASIC =================
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    # ================= ECONOMY =================
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

    # ================= FUN =================
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("hug", hug))
    app.add_handler(CommandHandler("punch", punch))
    app.add_handler(CommandHandler("kiss", kiss))
    app.add_handler(CommandHandler("couple", couple))

    # ================= GAME =================
    register_game_commands(app)

    # ================= ADMIN =================
    register_admin_commands(app)

    # ================= AI CHAT =================
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_message_handler))

    print("🤖 Bot is running...")
    app.run_polling(drop_pending_updates=True)

# ================== ENTRY ==================
if __name__ == "__main__":
    main()
