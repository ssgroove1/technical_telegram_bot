import telebot
import os

bot = telebot.TeleBot(os.getenv('TG_API_TOKEN')) # your bot API


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if message.text == '/help':
        bot.reply_to(message, "Если у вас возникли")
    else:
        bot.reply_to(message, """\
    Привет, Я бот генерации картинок по вашему запросу.
    """)