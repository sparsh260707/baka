from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# import commands
from commands.economy import bal, rob, kill, revive, protect

# ================== START COMMAND ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton("🎮 Open Game", url=f"https://t.me/{context.bot.username}")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
👋 Hey {user.first_name}!

Welcome to the 💰 *Economy Crime Game Bot* 😈

⚡ Earn money, rob users, kill enemies, buy protection and become the richest!

👇 Click below to start playing:
"""

    # If in group → send DM
    if update.message.chat.type != "private":
        await update.message.reply_text(
            "📩 Check your private chat to start the game!",
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
        # If already in private
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ================== MAIN ==================

def main():
    BOT_TOKEN = "8287968509:AAHLI0b1YGk0bfMIbSMOIQ4ETF68uNsBfos"

    app = Application.builder().token(BOT_TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bal", bal))
    app.add_handler(CommandHandler("rob", rob))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("revive", revive))
    app.add_handler(CommandHandler("protect", protect))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
