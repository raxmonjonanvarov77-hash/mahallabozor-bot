import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish")],
            [KeyboardButton(text="📦 Mening buyurtmalarim")],
            [KeyboardButton(text="☎️ Yordam")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "🛍 <b>MAHALLABOZOR</b>\n\n"
        "Mahallangizdagi magazindan mahsulotlarni "
        "uyingizgacha buyurtma qiling!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@dp.message()
async def all_messages(message: Message):
    if message.text == "🛒 Buyurtma berish":
        await message.answer(
            "🛒 Buyurtma berish bo‘limi tez orada ishga tushadi.\n\n"
            "Hozir biz birinchi magazin bilan tizimni sozlayapmiz."
        )

    elif message.text == "📦 Mening buyurtmalarim":
        await message.answer("📦 Sizda hozircha buyurtmalar mavjud emas.")

    elif message.text == "☎️ Yordam":
        await message.answer(
            "☎️ Yordam uchun administrator bilan bog‘laning."
        )


async def main():
    print("MAHALLABOZOR BOT ISHLAYAPTI!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
