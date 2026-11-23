import os
import telebot
from telebot import apihelper
from aiohttp import web

# Настройки
TOKEN = "1780243426:Hv3Oka1DuzTRSFrJcMVh0N4HNEu9wHAfgGE"
WEBAPP_URL = "https://anton1212xc-hue.github.io/anton1212-hue.github.io/"
PORT = int(os.environ.get("PORT", 10000))
ADMIN_ID = 1780243411  # Ваш Shuzagram ID

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
        
        # Отправляем админу
        bot.send_message(ADMIN_ID, text, parse_mode="HTML")
        # Отвечаем игроку
        bot.reply_to(message, "✅ Ваша заявка на вывод принята! Администратор скоро свяжется с вами.")
    except Exception as e:
        print(f"Ошибка web_app_data: {e}")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (защита от засыпания) ---
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

import threading
def run_web_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_web_server())
    loop.run_forever()

if __name__ == "__main__":
    # Запускаем пинг-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    print("Бот запущен на telebot + Shuzagram API!")
    # Запуск бесконечного получения сообщений
    bot.infinity_polling(skip_pending=True)
