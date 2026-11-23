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

# 1. Настраиваем кастомный API Shuzagram (без проблемного DefaultBotProperties)
shuzagram_server = TelegramAPIServer.from_base("https://api.shuzagram.com")
session = AiohttpSession(api=shuzagram_server)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# 2. Обработчик команды /start с кнопкой Mini App
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
        parse_html=True
    )

# 3. Веб-сервер для предотвращения засыпания на Render
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

# 4. Главная функция запуска
async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    print("Бот запущен на Shuzagram API!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
