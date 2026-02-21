import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

TOKEN = "8554399878:AAFn7Gc2Tk6ZMBZuBCdtyjEF9tYp3iSdOfE"
ADMIN_ID = 7567698406 

# PythonAnywhere bepul rejasi uchun proxy sozlamasi
session = AiohttpSession(proxy="http://proxy.server:3128")
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

CHANNELS = ["@learn_english_with_ali"] 

# MA'LUMOTLAR BAZASI
conn = sqlite3.connect("films.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS films (code TEXT PRIMARY KEY, file_id TEXT)")
conn.commit()

async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["member", "administrator", "creator"]:
                return True
        except Exception:
            pass
    return False

@dp.message(Command("start"))
async def start_handler(message: Message):
    if not await check_sub(message.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="A'zo bo'lish", url=f"https://t.me/{CHANNELS[0][1:]}")],
            [InlineKeyboardButton(text="Tekshirish", callback_data="check")]
        ])
        await message.answer("Botdan foydalanish uchun kanalimizga a'zo bo'ling!", reply_markup=kb)
        return
    await message.answer("Film kodini yuboring 🎬")

@dp.callback_query(F.data == "check")
async def check_handler(callback: CallbackQuery):
    if await check_sub(callback.from_user.id):
        await callback.message.edit_text("Rahmat! Endi film kodini yuboring 🎬")
    else:
        await callback.answer("Hali a'zo bo'lmagansiz! ❌", show_alert=True)

@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_film_handler(message: Message):
    if message.caption and message.caption.isdigit():
        code = message.caption
        file_id = message.video.file_id
        try:
            cursor.execute("INSERT INTO films (code, file_id) VALUES (?, ?)", (code, file_id))
            conn.commit()
            await message.answer(f"✅ Yangi kino qo'shildi! Kodi: {code}")
        except sqlite3.IntegrityError:
            await message.answer("❌ Bu kod bilan allaqachon kino qo'shilgan!")
    else:
        await message.answer("⚠️ Videoni yuborayotganda izohiga faqat raqamli kod yozing!")

@dp.message(F.text.isdigit())
async def search_film(message: Message):
    if not await check_sub(message.from_user.id):
        return
    cursor.execute("SELECT file_id FROM films WHERE code=?", (message.text,))
    result = cursor.fetchone()
    if result:
        await bot.send_video(chat_id=message.chat.id, video=result[0])
    else:
        await message.answer("Bunday kodli kino topilmadi ❌")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
