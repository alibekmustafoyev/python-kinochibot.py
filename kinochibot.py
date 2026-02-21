import os
import logging
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- FLASK SERVER (Render uchun majburiy) ---
app = Flask('')

@app.route('/')
def home():
    return "CinemaBox Bot is Live!"

def run():
    # Render portni avtomatik beradi, bo'lmasa 10000 ishlatiladi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# --- BOT ASOSIY QISMI ---
API_TOKEN = '8554399878:AAFn7Gc2Tk6ZMBZuBCdtyjEF9typ3isDOfE' # Tokeningiz
ADMIN_ID = 7567698406 # Sizning ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- MA'LUMOTLAR BAZASI (Vaqtinchalik) ---
# Eslatma: Render'da disk ulamasangiz, bot o'chib yonganda bu ma'lumotlar o'chadi
movies = {} 

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! CinemaBox botiga xush kelibsiz.\nKino kodini yuboring yoki admin bo'lsangiz yangi kino qo'shing.")

@dp.message_handler(commands=['add'], user_id=ADMIN_ID)
async def add_movie_start(message: types.Message):
    await message.reply("Kino qo'shish uchun format: /post [kod] [nomi]\nVa kinoni o'zini yuboring.")

# Kino kodini tekshirish logikasi
@dp.message_handler(lambda message: message.text.isdigit())
async def get_movie(message: types.Message):
    code = message.text
    if code in movies:
        await message.answer_video(movies[code]['file_id'], caption=movies[code]['caption'])
    else:
        await message.reply("Kechirasiz, bu kod bilan kino topilmadi.")

# Admin uchun kino yuklash (Video yuborilganda)
@dp.message_handler(content_types=['video'], user_id=ADMIN_ID)
async def handle_video(message: types.Message):
    # Bu yerda oddiygina oxirgi yuborilgan videoni saqlash logikasi
    await message.reply(f"Video qabul qilindi! File ID: {message.video.file_id}\nUni bazaga qo'shish uchun kod bering.")

if __name__ == '__main__':
    print("Bot ishga tushmoqda...")
    keep_alive() # Flask serverni alohida treda yoqish
    executor.start_polling(dp, skip_updates=True)
