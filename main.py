import telebot
import os, time, nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from dotenv import load_dotenv
from logic import DB_Manager
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

load_dotenv() # доступ к .env
nltk.download('punkt_tab') # установка для nltk
nltk.download('stopwords') # установка для nltk

bot = telebot.TeleBot(os.getenv('TG_API_TOKEN')) # your bot API

def questions_markup(rows, one_time_use=False, remove_markup="Отмена 🚫"): # Кнопки для частозадаваемых вопросов
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time_use)
    markup.row_width = 1
    for row in rows:
        markup.add(KeyboardButton(row))
    markup.add(KeyboardButton(remove_markup))
    return markup

def category_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row_width = 2
    markup.add(KeyboardButton("Доставка"))
    markup.add(KeyboardButton("Заказ"))
    return markup

def support_markup(): # Кнопки поддержки
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Доставка 📦", callback_data=f'delivery_'),
               InlineKeyboardButton("Заказ 🍎", callback_data=f'order_'),
               InlineKeyboardButton("Тех. Поддержка ⚙️", callback_data=f'technical_'))
    return markup

def back_markup(): # Кнопка вернуть
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Вернуться 📛", callback_data=f'back_'))
    return markup

def decline_markup(message_id=None, department=None): # Кнопка отклонить запрос
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Написать сообщение 💬", callback_data=f'message_{department}'), 
                InlineKeyboardButton("Отменить действия 🚫", callback_data=f'decline_{message_id}'))
    return markup

def vote_markup(): # Кнопка оценки ответа (в процессе)
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Да ✔️", callback_data=f'vote_like_'),
               InlineKeyboardButton("Нет ❌", callback_data=f'vote_dislike_'))
    return markup

def score_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Проблема решена? ✔️", callback_data=f'done_'),
               InlineKeyboardButton("Написать сообщение 💬", callback_data=f'continue_'))
    return markup

def techical_button():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Программисты (Работа с чат-ботом) 🔩", callback_data=f'support_programmer_'),
               InlineKeyboardButton("Отдел продаж (Работа с товарами/заказами) 📦", callback_data=f'support_sales_'))
    return markup

def department_button(department=None):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Написать сообщение 💬", callback_data=f'message_{department}'),
               InlineKeyboardButton("Изменить отдел 🛠️", callback_data=f'department_'))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("delivery_"): # Если пользователь нажал Доставка 📦
        questions = manager.get_question("Доставка")
        if questions: # Проверка, есть ли вопросы в бд
            questions = [x[0] for x in questions]
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=back_markup())
            bot.send_message(call.message.chat.id, f"<b>Выберите опцию.</b> 📦", parse_mode='HTML', reply_markup=questions_markup(questions))
        else:
            bot.send_message(call.message.chat.id, f"Возникла непредвиденная ошибка, свяжитесь с тех. поддержкой. 🧰\nError: Delivery_")

    elif call.data.startswith("order_"): # Если пользователь нажал Заказ 🍎
        questions = manager.get_question("Заказ")
        if questions: # Проверка, есть ли вопросы в бд
            questions = [x[0] for x in questions]
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=back_markup())
            bot.send_message(call.message.chat.id, f"<b>Выберите опцию.</b> 💍", parse_mode='HTML', reply_markup=questions_markup(questions))
        else:
            bot.send_message(call.message.chat.id, f"Возникла непредвиденная ошибка, свяжитесь с тех. поддержкой. 🧰\nError: Order_")

    elif call.data.startswith("vote_"): # Оценка ответов на частозадаваемые вопросы
        if call.data.startswith("vote_like_"):
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Спасибо за ваш отзыв! 🤗')
        else:
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.answer_callback_query(callback_query_id=call.id, text=f'Спасибо за ваш отзыв. 📝\nМы исправим этот недочёт! 🛠️')

    elif call.data.startswith("back_"): # Если нажата кнопка Вернуться 📛
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=support_markup())

    # Тех. поддержка
    elif call.data.startswith("done_"): # Завершения разговора с тех. поддержкой
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(callback_query_id=call.id, text=f'Мы рады, что наш ответ вам помог! 🤗')
        bot.send_message(call.message.chat.id, f'<b>Оцените качество ответа тех. поддержки</b> 💎', parse_mode='HTML')
        bot.register_next_step_handler(call.message, score_answer)

    elif call.data.startswith("continue_"): # Продолжение разговора с тех. поддержкой
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.answer_callback_query(callback_query_id=call.id, text=f'Мы с радостью решим ваш вопрос! 🛠️')
        bot.send_message(os.getenv('ADMIN'), f'<b>Пользователь, <code>{call.message.from_user.id}</code> продолжает разговор ⚙️</b>', parse_mode='HTML')
        bot.send_message(call.message.chat.id, f"<b>Отправьте сообщение для тех. поддержки.</b> ⚙️", parse_mode='HTML')

    elif call.data.startswith("department_"): # Изменение отдела поддержки
        bot.edit_message_text(f'<b>Выберите отдел тех. поддержки:</b> ⚙️', call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=techical_button())

    elif call.data.startswith("decline_"): # Отменить действия
        message_id = int(call.data[8:])
        bot.delete_message(call.message.chat.id, message_id=message_id)
        bot.send_message(call.message.chat.id, '<b>Действия отменены.</b> ⛔\n(<i>Для повтора введите: /menu </i>)', parse_mode='HTML')

    elif call.data.startswith('technical_'): # Первый шаг обращения к тех. поддержки
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=back_markup())
        bot_message = bot.send_message(call.message.chat.id, '<b>Генерирую текст.</b> ⏳', parse_mode='HTML')
        message_id = bot_message.message_id
        time.sleep(1)
        bot.edit_message_text(f'<b>Выберите отдел тех. поддержки:</b> ⚙️', call.message.chat.id, message_id, parse_mode='HTML', reply_markup=techical_button())
    
    elif call.data.startswith("support"): # Второй шаг обращения к тех. поддержки
        if call.data == 'support_programmer_': # Отдел программистов
            choice = f"Отдел Программистов 🔩"
        else: # Отдел продаж
            choice = f"Отдел продаж 📦"
        bot.edit_message_text(f"""<b>Выбран: {choice}</b>\n<blockquote>- Нажмите "Написать сообщение 💬", для связи с поддержкой ✉️\n<i>- Время ожидания поддержки 5-10 мин ⏱️</i></blockquote>""", call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=department_button(choice))

    elif call.data.startswith("message_"): # Третий шаг обращения к тех. поддержки
        department = str(call.data[8:])
        bot.edit_message_text(f"<blockquote>Отправьте сообщение с интересующим вас вопросом. 💬\n{'-'*75}\n<b>Пример оформления: 📝</b>\n<u>Ваше имя:</u> Алексей\n<u>Сообщение:</u> У меня возникли проблемы с оплатой...</blockquote>", call.message.chat.id, call.message.message_id, parse_mode='HTML')
        bot.register_next_step_handler(call.message, support_next_step, department=department)

def support_next_step(message, department): # Четвертый шаг обращения к тех. поддержки
    if message.text: # Если сообщение это текст
        text = message.text
        # Проверка текста
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('russian'))
        filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
        if len(filtered_tokens) >= 7: # Проверка, что текст не маленький
            bot.send_message(os.getenv('ADMIN'), f'<b>Был выбран отдел: {department} ⇩ ⇩ ⇩</b>', parse_mode='HTML')
            bot.forward_message(os.getenv('ADMIN'), message.chat.id, message.message_id) # Отправка сообщения в группу администрации (Вставьте свой айди)
            bot.send_message(message.chat.id, f'<b>Запрос в тех. поддержку успешно отправлен! 🌿\nВскоре вам ответят. ⏱️</b>', parse_mode='HTML')

            # Бот заполняет БД данными
            manager.add_message_from_user(user_id=message.from_user.id, category=department, message=text)
            if message.from_user.id not in [x[0] for x in manager.get_users()]:
                manager.add_user(user_id=message.from_user.id, username=message.from_user.username, first_name=message.from_user.first_name)
            else:
                pass
        else: # Слов недостаточно в сообщение
            bot_message = bot.send_message(message.chat.id, f"<b>Генерация.</b> ⏳", parse_mode='HTML')
            time.sleep(1)
            bot.edit_message_text(f"<b>Дополните предложение другими словами. ⛔\nВведите сообщение снова: 💬</b>", message.chat.id, bot_message.message_id, parse_mode='HTML', reply_markup=decline_markup(bot_message.message_id, department=department))
    elif message.voice: # Если сообщение голосовое
        # В будущем будет добавлены условия
        bot.send_message(os.getenv('ADMIN'), f'<b>Был выбран отдел: {department} ⇩ ⇩ ⇩</b>', parse_mode='HTML')
        bot.forward_message(os.getenv('ADMIN'), message.chat.id, message.message_id)
        bot.send_message(message.chat.id, f'<b>Запрос в тех. поддержку успешно отправлен! 🌿\nВскоре вам ответят. ⏱️</b>', parse_mode='HTML')

def score_answer(message): # Отзыв для тех. поддержки
    text = message.text
    bot.send_message(message.chat.id, f'<b>Спасибо за ваш отзыв!</b> 🤗', parse_mode='HTML')
    bot.send_message(os.getenv('ADMIN'), f'<b>Пользователь, <code>{message.from_user.id}</code> завершил разговор ✔️\nОтзыв:</b> {text}', parse_mode='HTML')

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start', 'menu'])
def send_welcome(message):
    if message.chat.id == int(os.getenv('ADMIN')): # Чат группы
        bot.send_message(message.chat.id, """
<b>Бот в сети! ✅
----------------------</b>
<b><i>Напоминалка:</i></b>
<blockquote>Сюда будут отправляться сообщения пользователей,
для ответа которых нужно ответить на сообщение пользователя. 🍍
/add_question - для добавления новых частозадаваемых вопросов.
/delete_question - для удаления существуещего вопроса.
</blockquote>""", parse_mode='HTML')
    else: # Если не чат группа
        start_message = bot.send_message(message.chat.id, '<b>Генерирую текст.</b> ⏳', parse_mode='HTML')
        message_id = start_message.message_id
        time.sleep(1)
        bot.edit_message_text(f"""
<b><i>Привет, {message.from_user.first_name}</i></b>! 👋
<blockquote>Я тех-бот интернет-магазина "Продаём всё на свете",
который ответит на интересующиеся вам вопросы. 🌟</blockquote>
<b>Выберите категорию поддержки.</b> ⚙️""", message.chat.id, message_id, parse_mode='HTML', reply_markup=support_markup())

@bot.message_handler(commands=['add_question']) # Первый шаг добавления нового ответа
def add_question_1(message):
    if message.chat.id == int(os.getenv('ADMIN')):
        bot.send_message(message.chat.id, f"Выберите категорию вопроса: 📝", reply_markup=category_markup())
        bot.register_next_step_handler(message, add_question_2)
    else:
        pass

def add_question_2(message): # Второй шаг добавления нового ответа
    category = message.text
    bot.send_message(message.chat.id, f'Напишите вопрос, по которому будет выдаваться ответ. ❓')
    bot.register_next_step_handler(message, add_question_3, category=category)

def add_question_3(message, category): # Третий шаг добавления нового ответа
    question = message.text
    bot.send_message(message.chat.id, f'Напишите ответ на ваш вопрос. 🔎')
    bot.register_next_step_handler(message, add_question_4, category=category, question=question)

def add_question_4(message, category, question): # Четвертый шаг добавления нового ответа
    answer = message.text
    manager.add_question(user_id=message.from_user.id, category=category, question=question, answer=answer)
    bot.send_message(message.chat.id, f'Готово! ✔️')

@bot.message_handler(commands=['delete_question']) # Первый шаг удаления вопроса
def delete_question_1(message):
    if message.chat.id == int(os.getenv('ADMIN')):
        questions = manager.get_question("Заказ", "Доставка")
        if questions: # Проверка, есть ли вопросы в бд
            questions = [x[0] for x in questions]
            bot.send_message(message.chat.id, f"Выберите вопрос, который нужно удалить: 📛", reply_markup=questions_markup(questions, True, ''))
            bot.register_next_step_handler(message, delete_question_2)
        else:
            bot.send_message(message.chat.id, f"Возникла непредвиденная ошибка. 🧰\nError: with manager.get_question()")
    else:
        pass

def delete_question_2(message): # Второй шаг удаления вопроса
    question = message.text
    manager.delete_question(question)
    bot.send_message(message.chat.id, f'Готово, вопрос удалён! 📌')

@bot.message_handler(func=lambda message:True)
def all_messages(message):
    if not message.chat.id == int(os.getenv('ADMIN')): # Чат группы
        if message.text == "Отмена 🚫": # Если текст от пользователя - это Отмена 🚫
            remove_markup = telebot.types.ReplyKeyboardRemove()
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, '<b>Действия отменены.</b> ⛔\n(<i>Для повтора введите: /menu </i>)', parse_mode='HTML', reply_markup=remove_markup)
        elif message.text in [x[0] for x in manager.get_question("Заказ", "Доставка")]: # Проверка, что пользователь отправил вопрос
            question = message.text
            answer = manager.get_answer(question)
            answer_message = bot.send_message(message.chat.id, f"<b>Готовлю ответ.</b> ⏳", parse_mode='HTML')
            message_id = answer_message.message_id
            time.sleep(1)
            bot.edit_message_text(f'<b>{question} 📝</b>\n<blockquote>{answer[0]}</blockquote>\nБыл ли этот ответ вам полезен? 📌', message.chat.id, message_id, parse_mode='HTML', reply_markup=vote_markup())
        else: # Любое сообщение
            bot.send_message(message.chat.id, "(<i>Пожалуйста, выберите категорию во вкладке /menu </i>)", parse_mode='HTML')
    else: # Чат основной группы тех. поддержки
        if message.reply_to_message:
            text = message.text
            user_id = message.reply_to_message.forward_from.id # Получаем айди пользователя из пересланного сообщения
            bot.send_message(user_id, f'<blockquote>- На связи администратор "Продаём всё на свете". 🛡️\n- Сообщение от администратора: 📝</blockquote>\n{text}', parse_mode='HTML', reply_markup=score_markup())

if __name__ == '__main__':
    manager = DB_Manager('database.db')
    bot.infinity_polling()