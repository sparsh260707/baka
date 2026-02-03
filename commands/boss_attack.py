import random
from telegram.ext import CommandHandler
from database.boss import boss_col

async def attack(update, context):
    chat = update.effective_chat
    user = update.effective_user

    event = boss_col.find_one({
        "group_id": chat.id,
        "status": "active"
    })

    if not event:
        await update.message.reply_text("❌ Koi active boss nahi hai.")
        return

    pid = str(user.id)
    if pid not in event["participants"]:
        await update.message.reply_text("❌ Tum registered nahi ho.")
        return

    dmg = random.randint(500, 2000)
    event["boss_hp"] -= dmg
    event["participants"][pid]["damage"] += dmg
    event["participants"][pid]["attacks"] += 1

    boss_col.update_one(
        {"_id": event["_id"]},
        {"$set": {
            "boss_hp": event["boss_hp"],
            "participants": event["participants"]
        }}
    )

    await update.message.reply_text(f"⚔️ Tumne {dmg} damage diya!")

def setup(app):
    app.add_handler(CommandHandler("attack", attack))
