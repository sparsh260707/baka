# utils.py
couples_db = {}  # Temporary dict; replace with actual DB if needed
images_db = {}

async def get_couple(chat_id, date):
    # Returns couple info if already selected for the day
    return couples_db.get((chat_id, date))

async def save_couple(chat_id, date, couple_data, img_url):
    couples_db[(chat_id, date)] = couple_data
    images_db[(chat_id, date)] = img_url

async def get_image(chat_id):
    # Returns saved image URL for the chat
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d/%m/%Y")
    return images_db.get((chat_id, today))
