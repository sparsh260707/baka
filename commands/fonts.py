# commands/fonts.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

# ===== FONT STYLES =====
class Fonts:
    @staticmethod
    def typewriter(text): return "".join([c + " " for c in text])
    @staticmethod
    def outline(text): return "".join([f"⟦{c}⟧" for c in text])
    @staticmethod
    def serif(text): return text
    @staticmethod
    def bold(text): return "".join([chr(ord(c)+0x1D3BF) if c.isalpha() else c for c in text])
    @staticmethod
    def small(text): return text.lower()
    @staticmethod
    def bubbles(text): return "".join([f"ⓑ{c}" for c in text])

# ===== KEYBOARD =====
def font_keyboard():
    buttons = [
        [
            InlineKeyboardButton("Typewriter", callback_data="font+typewriter"),
            InlineKeyboardButton("Outline", callback_data="font+outline"),
        ],
        [
            InlineKeyboardButton("Bold", callback_data="font+bold"),
            InlineKeyboardButton("Small", callback_data="font+small"),
        ],
        [
            InlineKeyboardButton("Bubbles", callback_data="font+bubbles"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)

# ===== /font =====
async def font(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗ Usage: /font Your Text")

    text = " ".join(context.args)

    await update.message.reply_text(
        f"🎨 Choose a font for:\n\n{text}",
        reply_markup=font_keyboard()
    )

# ===== BUTTON HANDLER =====
async def font_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("+")[1]
    original_text = query.message.text.split("\n\n", 1)[1]

    if data == "typewriter":
        new = Fonts.typewriter(original_text)
    elif data == "outline":
        new = Fonts.outline(original_text)
    elif data == "bold":
        new = Fonts.bold(original_text)
    elif data == "small":
        new = Fonts.small(original_text)
    elif data == "bubbles":
        new = Fonts.bubbles(original_text)
    else:
        new = original_text

    try:
        await query.message.edit_text(new, reply_markup=query.message.reply_markup)
    except:
        pass

# ===== REGISTER =====
def register_font_commands(app):
    app.add_handler(CommandHandler("font", font))
    app.add_handler(CommandHandler("fonts", font))
    app.add_handler(CallbackQueryHandler(font_button, pattern="^font\\+"))
