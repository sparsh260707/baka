from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN

# ================== IMPORT ECONOMY COMMANDS ==================
from commands.economy import bal, rob, kill, revive, protect

# ================== /START COMMAND ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Inline buttons (2x2 grid + 1 full-width button)
    keyboard = [
        [
            InlineKeyboardButton("💬 Talk to Baka", url="https://t.me/codebotnetwork"),
            InlineKeyboardButton("✨ Nobita K", url="https://t.me/oye_sparsh")
        ],
        [
            InlineKeyboardButton("🧸 Friends", url="https://t.me/codebotnetwork"),
            InlineKeyboardButton("🎮 Games", url=f"https://t.me/{context.bot.username}")
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

    # If command is used in a group/channel
    if update.effective_chat.type != "private":
        # Notify user to open private chat
        await update.message.reply_text(
            "📩 Check your private chat to start!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Open Private", url=f"https://t.me/{context.bot.username}")]
            ])
        )
        # Send main start message in private
        await context.bot.send_message(
            chat_id=user.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # Private chat: send start message directly
        await update.message.reply_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

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

    print("🤖 Bot is running...")
    app.run_polling()

# ================== RUN BOT ==================
if __name__ == "__main__":
    main()
