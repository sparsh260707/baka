# commands/font.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from utils import Fonts

USER_FONT_TEXT = {}

# ================= BUTTON PAGES =================

def font_page_1():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="font|typewriter"),
            InlineKeyboardButton("𝕆𝕦𝕥𝕝𝕚𝕟𝕖", callback_data="font|outline"),
            InlineKeyboardButton("𝐒𝐞𝐫𝐢𝐟", callback_data="font|serif"),
        ],
        [
            InlineKeyboardButton("𝑺𝒆𝒓𝒊𝒇", callback_data="font|bold_cool"),
            InlineKeyboardButton("𝑆𝑒𝑟𝑖𝑓", callback_data="font|cool"),
            InlineKeyboardButton("Sᴍᴀʟʟ Cᴀᴘs", callback_data="font|small_cap"),
        ],
        [
            InlineKeyboardButton("𝓈𝒸𝓇𝒾𝓅𝓉", callback_data="font|script"),
            InlineKeyboardButton("𝓼𝓬𝓻𝓲𝓹𝓽", callback_data="font|script_bolt"),
            InlineKeyboardButton("ᵗⁱⁿʸ", callback_data="font|tiny"),
        ],
        [
            InlineKeyboardButton("ᑕOᗰIᑕ", callback_data="font|comic"),
            InlineKeyboardButton("𝗦𝗮𝗻𝘀", callback_data="font|sans"),
            InlineKeyboardButton("𝙎𝙖𝙣𝙨", callback_data="font|slant_sans"),
        ],
        [
            InlineKeyboardButton("𝘚𝘢𝘯𝘴", callback_data="font|slant"),
            InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="font|sim"),
            InlineKeyboardButton("Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎", callback_data="font|circles"),
        ],
        [
            InlineKeyboardButton("🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎", callback_data="font|circle_dark"),
            InlineKeyboardButton("𝔊𝔬𝔱𝔥𝔦𝔠", callback_data="font|gothic"),
            InlineKeyboardButton("𝕲𝖔𝖙𝖍𝖎𝖈", callback_data="font|gothic_bolt"),
        ],
        [
            InlineKeyboardButton("C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡", callback_data="font|cloud"),
            InlineKeyboardButton("H̆̈ă̈p̆̈p̆̈y̆̈", callback_data="font|happy"),
            InlineKeyboardButton("S̑̈ȃ̈d̑̈", callback_data="font|sad"),
        ],
        [InlineKeyboardButton("➡️ Next", callback_data="font_page|2")],
    ])

def font_page_2():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇸 🇵 🇪 🇨 🇮 🇦 🇱 ", callback_data="font|special"),
            InlineKeyboardButton("🅂🅀🅄🄰🅁🄴🅂", callback_data="font|squares"),
            InlineKeyboardButton("🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎", callback_data="font|squares_bold"),
        ],
        [
            InlineKeyboardButton("ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ", callback_data="font|andalucia"),
            InlineKeyboardButton("爪卂几ᘜ卂", callback_data="font|manga"),
            InlineKeyboardButton("S̾t̾i̾n̾k̾y̾", callback_data="font|stinky"),
        ],
        [
            InlineKeyboardButton("B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ", callback_data="font|bubbles"),
            InlineKeyboardButton("U͟n͟d͟e͟r͟l͟i͟n͟e͟", callback_data="font|underline"),
            InlineKeyboardButton("꒒ꍏꀷꌩꌃꀎꁅ", callback_data="font|ladybug"),
        ],
        [
            InlineKeyboardButton("R҉a҉y҉s҉", callback_data="font|rays"),
            InlineKeyboardButton("B҈i҈r҈d҈s҈", callback_data="font|birds"),
            InlineKeyboardButton("S̸l̸a̸s̸h̸", callback_data="font|slash"),
        ],
        [
            InlineKeyboardButton("s⃠t⃠o⃠p⃠", callback_data="font|stop"),
            InlineKeyboardButton("S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆", callback_data="font|skyline"),
            InlineKeyboardButton("A͎r͎r͎o͎w͎s͎", callback_data="font|arrows"),
        ],
        [
            InlineKeyboardButton("ዪሀክቿነ", callback_data="font|qvnes"),
            InlineKeyboardButton("S̶t̶r̶i̶k̶e̶", callback_data="font|strike"),
            InlineKeyboardButton("F༙r༙o༙z༙e༙n༙", callback_data="font|frozen"),
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data="font_page|1")],
    ])

# ================= /font =================

async def font_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Kisi text ko reply karke /font likho")
        return

    USER_FONT_TEXT[update.effective_user.id] = update.message.reply_to_message.text

    await update.message.reply_text(
        "✨ Select font style:",
        reply_markup=font_page_1()
    )

# ================= CALLBACK =================

async def font_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data.startswith("font_page|"):
        page = data.split("|")[1]
        if page == "1":
            await query.edit_message_reply_markup(reply_markup=font_page_1())
        else:
            await query.edit_message_reply_markup(reply_markup=font_page_2())
        return

    if data.startswith("font|"):
        style = data.split("|")[1]

        if user_id not in USER_FONT_TEXT:
            await query.message.reply_text("❌ Text expired, dobara /font use karo")
            return

        text = USER_FONT_TEXT[user_id]

        cls = getattr(Fonts, style, None)
        if not cls:
            await query.message.reply_text("❌ Font not found")
            return

        new_text = cls(text)
        await query.message.edit_text(new_text, reply_markup=query.message.reply_markup)

# ================= REGISTER =================

def register_font_commands(app):
    app.add_handler(CommandHandler("font", font_cmd))
    app.add_handler(CallbackQueryHandler(font_callback, pattern="^font"))
    app.add_handler(CallbackQueryHandler(font_callback, pattern="^font_page"))
