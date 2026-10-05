
import asyncio
import os
import json

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# ==================================================
# SOZLAMALAR
# ==================================================

TOKEN = os.getenv("BOT_TOKEN")

# Railway Variables ichiga ADMIN_ID qo'yamiz
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

PRODUCTS_FILE = "products.json"


# ==================================================
# BOT
# ==================================================

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ==================================================
# MAHSULOTLARNI SAQLASH
# ==================================================

def load_products():
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return []


def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)


products = load_products()


# ==================================================
# ADMIN HOLATLARI
# ==================================================

class AddProduct(StatesGroup):
    name = State()
    price = State()
    quantity = State()
    category = State()
    photo = State()


# ==================================================
# MENYULAR
# ==================================================

def user_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Buyurtma berish")],
            [KeyboardButton(text="📦 Mening buyurtmalarim")],
            [KeyboardButton(text="☎️ Yordam")]
        ],
        resize_keyboard=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Mahsulot qo‘shish")],
            [KeyboardButton(text="📦 Mahsulotlar")],
            [KeyboardButton(text="🗑 Mahsulot o‘chirish")],
            [KeyboardButton(text="👤 Xaridor menyusi")]
        ],
        resize_keyboard=True
    )


# ==================================================
# START
# ==================================================

@dp.message(Command("start"))
async def start(message: Message):

    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 <b>MAHALLABOZOR ADMIN PANEL</b>\n\n"
            "Bu yerdan mahsulotlarni boshqarishingiz mumkin.",
            reply_markup=admin_menu(),
            parse_mode="HTML"
        )
        return

    await message.answer(
        "🛍 <b>MAHALLABOZOR</b>\n\n"
        "Mahallangizdagi magazindan mahsulotlarni "
        "uyingizgacha buyurtma qiling!",
        reply_markup=user_menu(),
        parse_mode="HTML"
    )


# ==================================================
# ADMIN: MAHSULOT QO'SHISH
# ==================================================

@dp.message(F.text == "➕ Mahsulot qo‘shish")
async def add_product_start(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📝 Mahsulot nomini yozing.\n\n"
        "Masalan:\n"
        "<b>Coca Cola 1.5L</b>",
        parse_mode="HTML"
    )

    await state.set_state(AddProduct.name)


@dp.message(AddProduct.name)
async def product_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer(
        "💰 Mahsulot narxini yozing.\n\n"
        "Masalan:\n"
        "<b>14000</b>",
        parse_mode="HTML"
    )

    await state.set_state(AddProduct.price)


@dp.message(AddProduct.price)
async def product_price(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer(
            "❌ Narx faqat raqam bo‘lishi kerak.\n\n"
            "Masalan: 14000"
        )
        return

    await state.update_data(price=int(message.text))

    await message.answer(
        "📦 Mahsulotdan nechta mavjud?\n\n"
        "Masalan: <b>20</b>",
        parse_mode="HTML"
    )

    await state.set_state(AddProduct.quantity)


@dp.message(AddProduct.quantity)
async def product_quantity(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer(
            "❌ Miqdor faqat raqam bo‘lishi kerak."
        )
        return

    await state.update_data(quantity=int(message.text))

    await message.answer(
        "🗂 Mahsulot kategoriyasini yozing.\n\n"
        "Masalan:\n"
        "🥤 Ichimliklar\n"
        "🍞 Non mahsulotlari\n"
        "🥛 Sut mahsulotlari"
    )

    await state.set_state(AddProduct.category)


@dp.message(AddProduct.category)
async def product_category(message: Message, state: FSMContext):

    await state.update_data(category=message.text)

    await message.answer(
        "📸 Endi mahsulot rasmini yuboring."
    )

    await state.set_state(AddProduct.photo)


@dp.message(AddProduct.photo, F.photo)
async def product_photo(message: Message, state: FSMContext):

    data = await state.get_data()

    photo_id = message.photo[-1].file_id

    product = {
        "id": len(products) + 1,
        "name": data["name"],
        "price": data["price"],
        "quantity": data["quantity"],
        "category": data["category"],
        "photo": photo_id
    }

    products.append(product)
    save_products(products)

    await state.clear()

    await message.answer(
        "✅ <b>Mahsulot muvaffaqiyatli qo‘shildi!</b>\n\n"
        f"🛍 {product['name']}\n"
        f"💰 {product['price']:,} so‘m\n"
        f"📦 {product['quantity']} dona\n"
        f"🗂 {product['category']}",
        reply_markup=admin_menu(),
        parse_mode="HTML"
    )


@dp.message(AddProduct.photo)
async def wrong_photo(message: Message):

    await message.answer(
        "📸 Iltimos, mahsulotning rasmini yuboring."
    )


# ==================================================
# ADMIN: MAHSULOTLARNI KO'RISH
# ==================================================

@dp.message(F.text == "📦 Mahsulotlar")
async def show_products(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    if not products:
        await message.answer(
            "📦 Hozircha mahsulotlar mavjud emas."
        )
        return

    for product in products:

        await bot.send_photo(
            message.chat.id,
            product["photo"],
            caption=(
                f"🛍 <b>{product['name']}</b>\n\n"
                f"💰 {product['price']:,} so‘m\n"
                f"📦 {product['quantity']} dona\n"
                f"🗂 {product['category']}"
            ),
            parse_mode="HTML"
        )
        if __name__ == "__main__":
    asyncio.run(main())
