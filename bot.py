from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from commands.economy import *

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("economy", economy))
app.add_handler(CommandHandler("bal", bal))
app.add_handler(CommandHandler("rob", rob))
app.add_handler(CommandHandler("kill", kill))
app.add_handler(CommandHandler("revive", revive))
app.add_handler(CommandHandler("protect", protect))
app.add_handler(CommandHandler("give", give))
app.add_handler(CommandHandler("toprich", toprich))

print("Bot running...")
app.run_polling()
