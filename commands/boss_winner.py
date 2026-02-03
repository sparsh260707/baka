from telegram.ext import CommandHandler
from database.boss import boss_col
from config import OWNER_ID

async def winner(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        return

    target = context.args[0]
    chat_id = update.effective_chat.id

    event = boss_col.find_one({"group_id": chat_id})
    if not event:
        return

    for uid, data in event["participants"].items():
        if target == uid or target.lstrip("@") == data.get("username"):
            boss_col.update_one(
                {"_id": event["_id"]},
                {"$set": {"winner": uid, "status": "ended"}}
            )
            await update.message.reply_text(f"🏆 Winner declared: {data.get('username')}")
            return

def setup(app):
    app.add_handler(CommandHandler("winner", winner))
