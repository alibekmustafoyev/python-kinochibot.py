import os
import logging
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. RENDER UCHUN FLASK QISMI ---
app = Flask(__name__)

@app.route('/')
def home():
    return "CinemaBox Bot is Live!"

def run():
    # Render avtomatik ravishda 10000-portni beradi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. BOT ASOSIY SOZLAMALARI ---
API_TOKEN = '8554399878:AAFn7Gc2Tk6ZMBZuBCdtyjEF9typ3isDOfE' # Tokeningiz
ADMIN_ID = 7567698406 # Sizning ID raqamingiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- 3. MA'LUMOTLAR BAZASI (VAQTINCHALIK) ---
# Diqqat: Render tekin tarifida bot o'chib yonganda bu ma'lumotlar o'chib ketadi.
# Doimiy saqlash uchun kelajakda SQLite yoki MongoDB ulaymiz.
movies = {}

# --- 4. BOT BUYRUQLARI ---

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        f"Salom {message.from_user.full_name}!\n"
        "Kinochibotga xush kelibsiz. Kino kodini yuboring."
    )

# Admin uchun kino qo'shish yo'riqnomasi
@dp.message_handler(commands=['add'], user_id=ADMIN_ID)
async def add_movie_help(message: types.Message):
    await message.answer("Kino qo'shish uchun videoni yuboring va izohiga kodini yozing.")

# Kino qidirish (Faqat raqam yuborilganda)
@dp.message_handler(lambda message: message.text.isdigit())
async def get_movie(message: types.Message):
    code = message.text
    if code in movies:
        movie = movies[code]
        await bot.send_video(
            message.chat.id, 
            movie['file_id'], 
            caption=f"🎬 Nomi: {movie['caption']}\n🆔 Kodi: {code}"
        )
    else:
        await message.reply("Afsuski, bu kod bilan kino topilmadi. 😔")

# Videolarni qabul qilish va bazaga saqlash (Faqat Admin uchun)
@dp.message_handler(content_types=['video'], user_id=ADMIN_ID)
async def handle_video(message: types.Message):
    video_id = message.video.file_id
    caption = message.caption if message.caption else "Nomsiz kino"
    
    # Videoni vaqtinchalik xotiraga saqlash
    # Format: Agar izohda "123 Kino nomi" bo'lsa, 123 - kod bo'ladi
    code = caption.split()[0]
    movies[code] = {'file_id': video_id, 'caption': caption}
    
    await message.reply(f"✅ Kino bazaga qo'shildi!\n🆔 Kodi: {code}\n🎬 Nomi: {caption}")

# --- 5. ISHGA TUSHIRISH ---
if __name__ == '__main__':
    # Flaskni alohida treda yoqamiz, bu Render uchun shart
    t = threading.Thread(target=run)
    t.start()
    
    print("Bot ishga tushmoqda...")
    executor.start_polling(dp, skip_updates=True)
