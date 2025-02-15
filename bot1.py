import os
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Конфигурация
TOKEN = "7422230592:AAGADhiy7BB2Cdd9yNZUcZlrl6gfMtKc6pg"
WEBHOOK_URL = "https://yourserver.com/webhook"
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 5000))

# База данных
conn = sqlite3.connect("guides.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS guides (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        price INTEGER,
        file_id TEXT
    )
""")
conn.commit()

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    cursor.execute("SELECT id, title, price FROM guides")
    guides = cursor.fetchall()
    for guide in guides:
        keyboard.add(InlineKeyboardButton(f"{guide[1]} - {guide[2]} руб.", callback_data=f"buy_{guide[0]}"))
    
    await message.answer("Выберите гайд:", reply_markup=keyboard)

# Обработчик кнопки покупки
@dp.callback_query(F.data.startswith("buy_"))
async def buy_guide(callback_query: types.CallbackQuery):
    guide_id = int(callback_query.data.split("_")[1])
    cursor.execute("SELECT title, price FROM guides WHERE id = ?", (guide_id,))
    guide = cursor.fetchone()
    if guide:
        await bot.send_message(callback_query.from_user.id, f"Для покупки {guide[0]} переведите {guide[1]} руб. и отправьте скриншот оплаты.")
    await callback_query.answer()

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

# Настройка веб-сервера
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
setup_application(app, dp, bot=bot, on_startup=[on_startup], on_shutdown=[on_shutdown])

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)