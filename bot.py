from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from config import BOT_TOKEN

# ================== IMPORT ECONOMY COMMANDS ==================
from commands.economy import bal, rob, kill, revive, protect

# ================== /START COMMAND ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Inline buttons (2x2 grid + 1 full-width button)
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

    # Fancy Unicode + Markdown styling
    text = f"""✨ 𝗛𝗲𝘆, *{user.first_name}* ~
💌 You're Talking To 𝓑𝓪𝓴𝓪, A _Sassy Cutie Girl_ 💕

👇 Choose An Option Below:"""

    # Group vs private chat handling
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
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ================== CALLBACK QUERY HANDLER ==================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge button press

    if query.data == "talk_baka":
        await query.message.reply_text("Hey Qt! How are you? 💕")

# ================== MAIN BOT SETUP ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bal", bal))
    app.add_handler(CommandHandler("rob", rob))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("revive", revive))
    app.add_handler(CommandHandler("protect", protect))

    # Callback for inline buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()

# ================== RUN BOT ==================
if __name__ == "__main__":
    main()
