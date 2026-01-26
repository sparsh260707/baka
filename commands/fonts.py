# commands/font.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

from utils import Fonts

FONT_PAGES = [
    [
        ("Bold", "bold"),
        ("Outline", "outline"),
        ("Typewriter", "typewriter"),
        ("SmallCaps", "smallcap"),
        ("Circles", "circles"),
        ("Dark Circles", "dark_circle"),
    ],
    [
        ("Bubbles", "bubbles"),
        ("Strike", "strike"),
        ("Underline", "underline"),
        ("Frozen", "frozen"),
        ("Slash", "slash"),
        ("Clouds", "clouds"),
    ],
    [
        ("Arrows", "arrows"),
        ("Skyline", "skyline"),
        ("Rays", "rays"),
        ("Birds", "birds"),
        ("Stop", "stop"),
        ("Sad", "sad"),
        ("Happy", "happy"),
    ]
]

def build_keyboard(page: int):
    buttons = []
    for name, key in FONT_PAGES[page]:
        buttons.append(InlineKeyboardButton(name, callback_data=f"font|{key}|{page}"))

    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Back", callback_data=f"fontpage|{page-1}"))
    if page < len(FONT_PAGES) - 1:
        nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"fontpage|{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="fontclose")])
    return InlineKeyboardMarkup(keyboard)


# ================= /font =================
async def font_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    text = None

    # Case 1: Reply mode
    if msg.reply_to_message and msg.reply_to_message.text:
        text = msg.reply_to_message.text

    # Case 2: /font something
    elif context.args:
        text = " ".join(context.args)

    if not text:
        await msg.reply_text("❌ Kisi text ko reply karke /font likho ya\n/font hello world")
        return

    await msg.reply_text(
        f"✨ Select a font for:\n\n{text}",
        reply_markup=build_keyboard(0)
    )


# ================= CALLBACK =================
async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "fontclose":
        await query.message.delete()
        return

    if data.startswith("fontpage|"):
        page = int(data.split("|")[1])
        await query.edit_message_reply_markup(reply_markup=build_keyboard(page))
        return

    if data.startswith("font|"):
        _, font_key, page = data.split("|")

        original_text = query.message.text.split("\n\n", 1)[1]

        func = getattr(Fonts, font_key)
        new_text = func(original_text)

        await query.edit_message_text(
            f"✨ Select a font for:\n\n{new_text}",
            reply_markup=build_keyboard(int(page))
        )


def register_font_commands(app):
    app.add_handler(font_handler)
    app.add_handler(font_callback_handler)
