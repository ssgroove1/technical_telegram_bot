import telebot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

load_dotenv() # доступ к .env

bot = telebot.TeleBot(os.getenv('TG_API_TOKEN')) # your bot API

def support_markup():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
    button1 = KeyboardButton("Доставка 📦")
    button2 = KeyboardButton("Заказ 🍎")
    button3 = KeyboardButton("Тех. Поддержка ⚙️")
    markup.add(button1, button2, button3)
    return markup

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    if message.chat.id == int(os.getenv('ADMIN')): # Чат группы
        bot.send_message(message.chat.id, """
<b>Бот в сети! ✅
----------------------</b>
<b><i>Напоминалка:</i></b>
<blockquote>Сюда будут отправляться сообщения пользователей,
для ответа которых нужно ответить на сообщение пользователя. 🍍</blockquote>""", parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, f"""
<b><i>Привет, {message.from_user.first_name}</i></b>! 👋
<blockquote>Я тех-бот интернет-магазина "Продаём всё на свете",
который ответит на интересующиеся вам вопросы. 🌟</blockquote>
<b>Выберите категорию поддержки.</b> ⚙️""", parse_mode='HTML', reply_markup=support_markup())

if __name__ == '__main__':
    bot.infinity_polling()