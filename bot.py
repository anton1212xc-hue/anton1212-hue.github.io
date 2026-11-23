import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

# Настройки
TOKEN = "1780243426:Hv3Oka1DuzTRSFrJcMVh0N4HNEu9wHAfgGE"
WEBAPP_URL = "https://anton1212xc-hue.github.io/anton1212-hue.github.io/"
PORT = 10000

# Укажите ваш числовой Telegram ID, чтобы заявки на вывод приходили вам в личку
ADMIN_ID = 000000000  # <--- Замените на ваш ID

# Создаем кастомный сервер API через явное указание base и file (обход проверки pydantic)
shuzagram_server = TelegramAPIServer(
    base="https://api.shuzagram.com/bot{token}/{method}",
    file="https://api.shuzagram.com/file/bot{token}/{path}"
)

session = AiohttpSession(api=shuzagram_server)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# Команда /start
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Открыть StarDrop", 
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    
    await message.answer(
        "👋 <b>Добро пожаловать в StarDrop!</b>\n\n"
        "Нажмите на кнопку ниже, чтобы запустить игру, крутить апгрейды и управлять балансом.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Обработка данных при нажатии кнопки «Вывести» в Mini App
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        data = message.web_app_data.data
        user = message.from_user
        
        text = (
            "📦 <b>Новая заявка на вывод!</b>\n\n"
            f"👤 Игрок: {user.full_name} (@{user.username or 'нет'})\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📊 Данные: {data}"
        )
        
        # Отправляем уведомление администратору
        if ADMIN_ID != 0:
            await bot.send_message(ADMIN_ID, text, parse_mode="HTML")
            
        # Отправляем подтверждение игроку в чат с ботом
        await message.answer("✅ Ваша заявка на вывод принята! Администратор скоро свяжется с вами.")
    except Exception as e:
        logging.error(f"Ошибка обработки Web App data: {e}")

# Веб-сервер для предотвращения засыпания на Render
async def handle_ping(request):
    return web.Response(text="Bot is alive and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Веб-сервер запущен на порту {PORT}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    print("Бот успешно запущен на Shuzagram API!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
