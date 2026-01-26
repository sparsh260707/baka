# commands/fonts.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

# ========== Simple Font Maps ==========
def typewriter(text): return "".join(chr(ord(c) + 0x1D670 - 0x41) if "A" <= c <= "Z" else chr(ord(c) + 0x1D68A - 0x61) if "a" <= c <= "z" else c for c in text)
def bold(text): return "".join(chr(ord(c) + 0x1D400 - 0x41) if "A" <= c <= "Z" else chr(ord(c) + 0x1D41A - 0x61) if "a" <= c <= "z" else c for c in text)
def monospace(text): return "".join(chr(ord(c) + 0x1D670 - 0x41) if "A" <= c <= "Z" else chr(ord(c) + 0x1D68A - 0x61) if "a" <= c <= "z" else c for c in text)
def circle(text): return "".join(chr(ord(c) + 0x24B6 - 0x41) if "A" <= c <= "Z" else chr(ord(c) + 0x24D0 - 0x61) if "a" <= c <= "z" else c for c in text)

FONTS = {
    "typewriter": typewriter,
    "bold": bold,
    "mono": monospace,
    "circle": circle,
}

# ========== Keyboard ==========
def font_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="font+typewriter"),
            InlineKeyboardButton("𝗕𝗼𝗹𝗱", callback_data="font+bold"),
        ],
        [
            InlineKeyboardButton("𝙼𝚘𝚗𝚘", callback_data="font+mono"),
            InlineKeyboardButton("Ⓒⓘⓡⓒⓛⓔ", callback_data="font+circle"),
        ]
    ])

# ========== /font command ==========
async def font_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❗ Use: /font Your text")

    text = " ".join(context.args)
   await update.message.reply_text(
    text,
    reply_markup=font_keyboard()
)

# ========== Callback ==========
async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if not data.startswith("font+"):
        return

    style = data.split("+")[1]

    func = FONTS.get(style)
    if not func:
        return

    original = query.message.text
    new_text = func(original)

    try:
        await query.message.edit_text(new_text, reply_markup=query.message.reply_markup)
    except:
        pass

# ========== Register ==========
def register_font_commands(app):
    app.add_handler(CommandHandler("font", font_cmd))
    app.add_handler(CommandHandler("fonts", font_cmd))
    app.add_handler(CallbackQueryHandler(font_callback, pattern="^font\\+"))
