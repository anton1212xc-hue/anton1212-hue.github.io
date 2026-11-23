import os
import time
import threading
import asyncio
import requests
import telebot
from telebot import apihelper
from aiohttp import web

# Настройки
TOKEN = "1780243426:Hv3Oka1DuzTRSFrJcMVh0N4HNEu9wHAfgGE"
WEBAPP_URL = "https://anton1212xc-hue.github.io/anton1212-hue.github.io/"
PORT = int(os.environ.get("PORT", 10000))
ADMIN_ID = 1780243411  # Ваш Shuzagram ID

# Получаем публичный URL вашего сервиса на Render (render автоматически задает переменные или подставьте ваш URL)
# Например: "https://anton1212-hue-github-io.onrender.com"
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL", "")

# Перенаправляем все запросы pyTelegramBotAPI на кастомный сервер Shuzagram
apihelper.API_URL = "https://api.shuzagram.com/bot{0}/{1}"

bot = telebot.TeleBot(TOKEN)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo(url=WEBAPP_URL)
    markup.add(telebot.types.InlineKeyboardButton(text="🎮 Открыть StarDrop", web_app=web_app))
    
    bot.reply_to(
        message, 
        "👋 <b>Добро пожаловать в StarDrop!</b>\n\n"
        "Нажмите на кнопку ниже, чтобы запустить игру, крутить апгрейды и управлять балансом.",
        reply_markup=markup,
        parse_mode="HTML"
    )

# Обработка данных из Mini App (заявка на вывод)
@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = message.web_app_data.data
        user = message.from_user
        
        text = (
            "📦 <b>Новая заявка на вывод!</b>\n\n"
            f"👤 Игрок: {user.first_name} (@{user.username or 'нет'})\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📊 Данные: {data}"
        )
        
        bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        bot.reply_to(message, "✅ Ваша заявка на вывод принята! Администратор скоро свяжется с вами.")
    except Exception as e:
        print(f"Ошибка web_app_data: {e}")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
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

def run_web_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_web_server())
    loop.run_forever()

# --- ФОНОВЫЙ САМОПИНГЕР (Каждые 30 секунд) ---
def self_ping_worker():
    """Каждые 30 секунд стучится на собственный сервер Render, чтобы не дать ему уснуть"""
    time.sleep(10)  # Даем серверу время запуститься
    while True:
        try:
            if RENDER_EXTERNAL_URL:
                requests.get(RENDER_EXTERNAL_URL, timeout=10)
                print("[Self-Ping] Успешный пинг самого себя")
        except Exception as e:
            print(f"[Self-Ping] Ошибка пинга: {e}")
        time.sleep(30)  интервал 30 секунд

if __name__ == "__main__":
    # 1. Запускаем веб-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()

    # 2. Запускаем фоновый поток самопробуждения каждые 30 секунд
    ping_thread = threading.Thread(target=self_ping_worker, daemon=True)
    ping_thread.start()
    
    print("Бот запущен на telebot + Shuzagram API с системой самопробуждения!")
    # 3. Запуск бесконечного получения сообщений
    bot.infinity_polling(skip_pending=True)
