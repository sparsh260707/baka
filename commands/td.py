# commands/td.py
import httpx
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# API endpoints
TRUTH_API_URL = "https://api.truthordarebot.xyz/v1/truth"
DARE_API_URL = "https://api.truthordarebot.xyz/v1/dare"

# ===================== TRUTH COMMAND =====================
async def get_truth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(TRUTH_API_URL)
        if response.status_code == 200:
            data = response.json()
            question = data.get("question", "No question found!")
            await update.message.reply_text(f"ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ:\n\n{question}")
        else:
            await update.message.reply_text(
                "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀ ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
            )
    except Exception as e:
        await update.message.reply_text(
            "ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴀ ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
        )

# ===================== DARE COMMAND =====================
async def get_dare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(DARE_API_URL)
        if response.status_code == 200:
            data = response.json()
            question = data.get("question", "No question found!")
            await update.message.reply_text(f"ᴅᴀʀᴇ ǫᴜᴇsᴛɪᴏɴ:\n\n{question}")
        else:
            await update.message.reply_text(
                "ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀ ᴅᴀʀᴇ ǫᴜᴇsᴛɪᴏɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
            )
    except Exception as e:
        await update.message.reply_text(
            "ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴀ ᴅᴀʀᴇ ǫᴜᴇsᴛɪᴏɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."
        )

# ===================== HELP INFO =====================
__HELP__ = """
**ᴛʀᴜᴛʜ ᴏʀ ᴅᴀʀᴇ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅs**

Use these commands to play Truth or Dare:

- `/truth` : Get a random truth question. Answer honestly!
- `/dare` : Get a random dare challenge. Complete it if you dare!

**Examples:**
- `/truth`: "What is your most embarrassing moment?"
- `/dare`: "Do 10 push-ups."

**Note:**
If you encounter any issues fetching questions, please try again later.
"""

__MODULE__ = "Tʀᴜᴛʜ"
