from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN

# commands
from commands.economy import bal, rob, kill, revive, protect

# ================== START ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Inline buttons: Update, Support, Owner
    keyboard = [
        [
            InlineKeyboardButton("🎮 Update", url=f"https://t.me/codebotnetwork"),
            InlineKeyboardButton("🛠 Support", url="https://t.me/codebotnetwork"),  # replace with your support link
            InlineKeyboardButton("👤 Owner", url="https://t.me/oye_sparsh")  # replace with owner's username
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"""
👋 Hey {user.first_name}!

Welcome to the 💰 *Economy Crime Game Bot* 😈

👇 Click below to start playing:
"""

    # If the command is used in a group/channel
    if update.message.chat.type != "private":
        # Tell user to check private chat
        await update.message.reply_text(
            "📩 Check your private chat to start the game!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Open Private", url=f"https://t.me/{context.bot.username}")]
            ])
        )

        # Send the main start message in private
        await context.bot.send_message(
            chat_id=user.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        # If command used in private chat, just send the start message
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ================== MAIN ==================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
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
