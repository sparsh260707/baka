# bot.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
)
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ================== IMPORT DATABASE & COMMANDS ==================
from database.db import get_user

# Economy
from commands.economy import (
    bal, rob, kill, revive, protect, give, myrank, toprich,
    leaders, economy, open_economy, close_economy
)

# Other modules
from commands.game import register_game_commands
from commands.admin import register_admin_commands
from commands.chatbot import ask_ai, ai_message_handler
from commands.couple import couple_of_the_day
from commands.shop import items, item, gift
from commands.quote import q
from commands.td import get_truth, get_dare

# Fun
from commands.fun import (
    slap, hug, punch, kiss, bite, crush, brain, id_cmd, love, stupid_meter
)

# ================== START IMAGE ==================
START_IMAGE_URL = "https://files.catbox.moe/yzpfuh.jpg"

# ================== AUTO REGISTER ==================
async def auto_register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        if user and not user.is_bot and chat:
            get_user(user, chat.id)
    except Exception as e:
        print(f"❌ Registration Error: {e}")

# ================== /START ==================
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

    text = f"✨ 𝗛𝗲𝘆, *{user.first_name}* ~\n💌 You're Talking To 𝓑𝓪𝓴𝓪, A _Sassy Cutie Girl_ 💕"

    if update.effective_chat.type != "private":
        return await update.message.reply_text(
            "📩 Check your private chat to start!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Open Private", url=f"https://t.me/{context.bot.username}")]
            ])
        )

    await update.message.reply_photo(
        photo=START_IMAGE_URL,
        caption=text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# ================== BUTTON ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "talk_baka":
        await query.message.reply_text("Main thik hu, tum kaise ho? 😊")

# ================== ERROR HANDLER ==================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"❌ Critical Bot Error: {context.error}")

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Auto register (priority)
    app.add_handler(MessageHandler(filters.ALL, auto_register_handler), group=-1)

    # Start & buttons
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    # ===== Economy =====
    app.add_handler(CommandHandler("bal", bal))
    app.add_handler(CommandHandler("q", q))
    app.add_handler(CommandHandler("rob", rob))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("revive", revive))
    app.add_handler(CommandHandler("protect", protect))
    app.add_handler(CommandHandler("give", give))
    app.add_handler(CommandHandler("myrank", myrank))
    app.add_handler(CommandHandler("toprich", toprich))
    app.add_handler(CommandHandler("leaders", leaders))
    app.add_handler(CommandHandler("economy", economy))
    app.add_handler(CommandHandler("open", open_economy))
    app.add_handler(CommandHandler("close", close_economy))

    # ===== Shop =====
    app.add_handler(CommandHandler("items", items))
    app.add_handler(CommandHandler("item", item))
    app.add_handler(CommandHandler("gift", gift))

    # ===== Truth & Dare =====
    app.add_handler(CommandHandler("truth", get_truth))
    app.add_handler(CommandHandler("dare", get_dare))

     # ===== Fun =====
    app.add_handler(CommandHandler("slap", slap))
    app.add_handler(CommandHandler("hug", hug))
    app.add_handler(CommandHandler("punch", punch))
    app.add_handler(CommandHandler("kiss", kiss))
    app.add_handler(CommandHandler("bite", bite))
    app.add_handler(CommandHandler("love", love))
    app.add_handler(CommandHandler("stupid_meter", stupid_meter))
    app.add_handler(CommandHandler("crush", crush))
    app.add_handler(CommandHandler("brain", brain))
    app.add_handler(CommandHandler("id", id_cmd))

    # ===== Couple =====
    app.add_handler(CommandHandler("couple", couple))

    # ===== Game & Admin =====
    register_game_commands(app)
    register_admin_commands(app)

    # ===== AI Chat =====
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_message_handler))

    print("🤖 Baka Bot is online and watching over you!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
