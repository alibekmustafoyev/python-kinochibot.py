import os
import logging
import threading
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# --- 1. RENDER UCHUN FLASK (TEKIN TARIF SHARTI) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "CinemaBox Bot ishlamoqda! ✅"

def run():
    # Render avtomatik 10000-portni beradi, bo'lmasa 10000 ishlatiladi
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. BOT ASOSIY SOZLAMALARI ---
API_TOKEN = '8554399878:AAFn7Gc2Tk6ZMBZuBCdtyjEF9typ3isDOfE' # Botingiz tokeni
ADMIN_ID = 7567698406 # Sizning Telegram ID raqamingiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- 3. KINO BAZASI (Xotirada saqlash) ---
# Diqqat: Render tekin tarifda botni qayta yuklasa, bu ma'lumotlar o'chishi mumkin.
movies = {}

# --- 4. BOT FUNKSIYALARI ---

# Start buyrug'i
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(f"Salom {message.from_user.first_name}! 👋\n\nKino kodini yuboring va men uni sizga topib beraman.")

# Admin uchun yordam
@dp.message_handler(commands=['add'], user_id=ADMIN_ID)
async def admin_help(message: types.Message):
    await message.answer("Kino qo'shish tartibi:\n1. Videoni yuboring.\n2. Izohiga (caption) raqamli kod yozing.")

# Kino qidirish (Raqam yozilsa)
@dp.message_handler(lambda message: message.text.isdigit())
async def search_movie(message: types.Message):
    code = message.text
    if code in movies:
        movie = movies[code]
        await bot.send_video(
            message.chat.id, 
            movie['file_id'], 
            caption=f"🎬 Kino nomi: {movie['caption']}\n🆔 Kod: {code}"
        )
    else:
        await message.answer("Afsuski, bu kod bilan kino topilmadi. 😔")

# Videoni qabul qilish va bazaga qo'shish (Faqat Admin)
@dp.message_handler(content_types=['video'], user_id=ADMIN_ID)
async def save_movie(message: types.Message):
    if message.caption and message.caption.isdigit():
        code = message.caption
        movies[code] = {
            'file_id': message.video.file_id,
            'caption': f"Kino #{code}" # Bu yerga nomini ham qo'shsa bo'ladi
        }
        await message.reply(f"✅ Kino bazaga qo'shildi!\nKodi: {code}")
    else:
        await message.reply("❌ Xato! Videoga izoh sifatida faqat raqamli kod yozing.")

# --- 5. ISHGA TUSHIRISH ---
if __name__ == '__main__':
    # Flaskni treda yoqish (Render 502 xatosini bermasligi uchun)
    t = threading.Thread(target=run)
    t.start()
    
    print("Bot Render'da ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)
