import os
import logging
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- RENDER UCHUN FLASK (PORTNI TO'G'RI BOG'LASH) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "CinemaBox Bot is Live!"

def run():
    # Render'da port 10000 bo'lishi shart
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- BOT SOZLAMALARI ---
API_TOKEN = '8554399878:AAFn7Gc2Tk6ZMBZuBCdtyjEF9typ3isDOfE'
ADMIN_ID = 7567698406

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- KINO BAZASI (XOTIRADA) ---
movies = {}

# --- BOT FUNKSIYALARI ---

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Salom! Kino kodini yuboring.")

@dp.message_handler(commands=['add'], user_id=ADMIN_ID)
async def add_help(message: types.Message):
    await message.answer("Kino qo'shish: Videoni yuboring va izohiga kodini yozing.")

# Kino qidirish (Raqam yozilsa)
@dp.message_handler(lambda message: message.text.isdigit())
async def search(message: types.Message):
    code = message.text
    if code in movies:
        m = movies[code]
        await bot.send_video(message.chat.id, m['id'], caption=f"🎬 Kod: {code}")
    else:
        await message.answer("Topilmadi.")

# Videoni saqlash (Admin uchun)
@dp.message_handler(content_types=['video'], user_id=ADMIN_ID)
async def save(message: types.Message):
    if message.caption and message.caption.isdigit():
        movies[message.caption] = {'id': message.video.file_id}
        await message.reply(f"✅ Saqlandi: {message.caption}")
    else:
        await message.reply("❌ Izohga faqat raqamli kod yozing.")

if __name__ == '__main__':
    # Flaskni alohida treda yoqamiz
    threading.Thread(target=run).start()
    executor.start_polling(dp, skip_updates=True)
