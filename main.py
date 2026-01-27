import telebot
import os, time
from dotenv import load_dotenv
from logic import DB_Manager
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

load_dotenv() # доступ к .env

bot = telebot.TeleBot(os.getenv('TG_API_TOKEN')) # your bot API

def questions_markup(rows):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton("Отмена 🚫"))
    return markup

def support_markup(message_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Доставка 📦", callback_data=f'delivery_{message_id}'),
               InlineKeyboardButton("Заказ 🍎", callback_data=f'order_{message_id}'),
               InlineKeyboardButton("Тех. Поддержка ⚙️", callback_data=f'technical_{message_id}'))
    return markup

def back_markup(message_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Вернуться 📛", callback_data=f'back_{message_id}'))
    return markup

def vote_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Отлично ✔️", callback_data=f'like_'),
               InlineKeyboardButton("Ужасно ❌", callback_data=f'dislike_'))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("delivery_"):
        message_id = int(call.data[9:])
        questions = manager.get_question("Доставка")
        if questions:
            questions = [x[0] for x in questions]
            bot.edit_message_reply_markup(call.message.chat.id, message_id, reply_markup=back_markup(message_id))
            bot.send_message(call.message.chat.id, f"<b>Выберите опцию.</b> 📦", parse_mode='HTML', reply_markup=questions_markup(questions))
        else:
            bot.send_message(call.message.chat.id, f"Возникла непредвиденная ошибка, свяжитесь с тех. поддержкой. 🧰")
    elif call.data.startswith("back_"):
        message_id = int(call.data[5:])
        bot.edit_message_reply_markup(call.message.chat.id, message_id, reply_markup=support_markup(message_id))


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
        start_message = bot.send_message(message.chat.id, '<b>Генерирую текст.</b> ⏳', parse_mode='HTML')
        message_id = start_message.message_id
        time.sleep(1)
        bot.edit_message_text(f"""
<b><i>Привет, {message.from_user.first_name}</i></b>! 👋
<blockquote>Я тех-бот интернет-магазина "Продаём всё на свете",
который ответит на интересующиеся вам вопросы. 🌟</blockquote>
<b>Выберите категорию поддержки.</b> ⚙️""", message.chat.id, message_id, parse_mode='HTML', reply_markup=support_markup(message_id))
        
@bot.message_handler(func=lambda message:True)
def all_messages(message):
    if message.text == "Отмена 🚫":
        remove_markup = telebot.types.ReplyKeyboardRemove()
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, '<b>Действия отменены. ⛔</b>', parse_mode='HTML', reply_markup=remove_markup)
    else:
        question = message.text
        answer = manager.get_answer(question)
        bot.send_message(message.chat.id, f'<b>{question} 📝</b>\n<blockquote>{answer[0]}</blockquote>\nБыл ли этот ответ вам полезен? 📌', parse_mode='HTML', reply_markup=vote_markup())

if __name__ == '__main__':
    manager = DB_Manager('database.db')
    bot.infinity_polling()