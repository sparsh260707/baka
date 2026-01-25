# commands/shop.py
# Shop + Gift + Inventory System for BAKA Bot

from telegram import Update
from telegram.ext import ContextTypes
from database.db import users_col, get_user
from commands.economy import can_use_economy, update_user_data

# 🛍️ SHOP ITEMS
SHOP_ITEMS = {
    "rose": {"name": "🌹 Rose", "price": 500},
    "chocolate": {"name": "🍫 Chocolate", "price": 800},
    "ring": {"name": "💍 Ring", "price": 2000},
    "teddy": {"name": "🧸 Teddy Bear", "price": 1500},
    "pizza": {"name": "🍕 Pizza", "price": 600},
    "surprise": {"name": "🎁 Surprise Box", "price": 2500},
    "puppy": {"name": "🐶 Puppy", "price": 3000},
    "cake": {"name": "🎂 Cake", "price": 1000},
    "letter": {"name": "💌 Love Letter", "price": 400},
    "cat": {"name": "🐱 Cat", "price": 2500},
}

# ================= /items =================
async def items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): 
        return

    text = "🛍️ Available Items\n\n"
    for k, v in SHOP_ITEMS.items():
        text += f"{v['name']} — ${v['price']}\n"

    await update.message.reply_text(text)

# ================= /item =================
async def item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): 
        return

    user_obj = update.effective_user
    if update.message.reply_to_message:
        user_obj = update.message.reply_to_message.from_user

    user = get_user(user_obj)

    inv = user.get("inventory", {})

    if not inv:
        return await update.message.reply_text("📦 Inventory is empty.")

    text = f"📦 {user.get('name','User')}'s Inventory:\n\n"
    for k, c in inv.items():
        item_name = SHOP_ITEMS.get(k, {}).get("name", k)
        text += f"{item_name} × {c}\n"

    await update.message.reply_text(text)

# ================= /gift =================
async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await can_use_economy(update, context): 
        return

    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to gift!")

    if not context.args:
        return await update.message.reply_text("Usage: /gift <item name>")

    key = context.args[0].lower()

    if key not in SHOP_ITEMS:
        return await update.message.reply_text("❌ Item not found. Use /items")

    sender_user = update.effective_user
    receiver_user = update.message.reply_to_message.from_user

    sender = get_user(sender_user)
    receiver = get_user(receiver_user)

    price = SHOP_ITEMS[key]["price"]

    if sender.get("bal", 0) < price:
        return await update.message.reply_text("❌ Not enough balance!")

    # Deduct money
    sender["bal"] -= price

    # Add to receiver inventory
    if "inventory" not in receiver:
        receiver["inventory"] = {}

    receiver["inventory"][key] = receiver["inventory"].get(key, 0) + 1

    update_user_data(sender_user.id, sender)
    update_user_data(receiver_user.id, receiver)

    await update.message.reply_text(
        f"🎁 {sender.get('name','Someone')} gifted {SHOP_ITEMS[key]['name']} to {receiver.get('name','User')}!"
    )
