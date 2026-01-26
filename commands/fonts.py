# commands/font.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

from utils import Fonts

# All font functions list (page wise)
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
        buttons.append(
            InlineKeyboardButton(name, callback_data=f"font|{key}|{page}")
        )

    # 2 buttons per row
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


# ================= /font command =================
async def font_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /font hello world")
        return

    text = " ".join(context.args)

    await update.message.reply_text(
        f"✨ Select a font for:\n\n{text}",
        reply_markup=build_keyboard(0)
    )


# ================= CALLBACK HANDLER =================
async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # Close
    if data == "fontclose":
        await query.message.delete()
        return

    # Page change
    if data.startswith("fontpage|"):
        page = int(data.split("|")[1])
        await query.edit_message_reply_markup(reply_markup=build_keyboard(page))
        return

    # Apply font
    if data.startswith("font|"):
        _, font_key, page = data.split("|")

        original_text = query.message.text.split("\n\n", 1)[1]

        # Call function dynamically from Fonts class
        func = getattr(Fonts, font_key)
        new_text = func(original_text)

        await query.edit_message_text(
            f"✨ Select a font for:\n\n{new_text}",
            reply_markup=build_keyboard(int(page))
        )


# ================= HANDLERS =================
font_handler = CommandHandler("font", font_cmd)
font_callback_handler = CallbackQueryHandler(font_callback, pattern="^font")
