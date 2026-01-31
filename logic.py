import sqlite3

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER,
                            username TEXT,
                            first_name TEXT,
                            FOREIGN KEY(user_id) REFERENCES messages(user_id)
                        )''')
            conn.execute('''CREATE TABLE messages (
                            user_id INTEGER,
                            status TEXT NOT NULL,
                            category TEXT NOT NULL,
                            message TEXT NOT NULL
                        )''')
            conn.execute('''CREATE TABLE questions (
                            count INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            category TEXT,
                            question TEXT,
                            answer TEXT
                        )''')
            
    def get_question(self, category, extra_category=None): # Получает вопросы всех категорий
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor() 
            cur.execute('SELECT question FROM questions WHERE category = ? OR category = ?', (category, extra_category))
            return cur.fetchall()
        
    def get_answer(self, question): # Получает ответ на вопрос
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor() 
            cur.execute('SELECT answer FROM questions WHERE question = ?', (question,))
            return cur.fetchall()[0]
        
    def get_users(self): # Изучает список пользователей
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor() 
            cur.execute('SELECT user_id FROM users')
            return cur.fetchall()
        
    def add_message_from_user(self, user_id=None, status="Не завершен 🚫", category='', message=''): # Добавляет сообщение в БД
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO messages VALUES (?, ?, ?, ?)', (user_id, status, category, message))
            conn.commit()

    def add_user(self, user_id='', username='', first_name=''): # Регистирует пользователя
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO users VALUES (?, ?, ?)', (user_id, username, first_name))
            conn.commit()

    def add_question(self, count=None, user_id=None, category='', question='', answer=''): # Добавление вопроса и ответа
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO questions VALUES (?, ?, ?, ?, ?)', (count, user_id, category, question, answer))
            conn.commit()
        
    def delete_question(self, question): # Удаление существующего вопроса
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('DELETE FROM questions WHERE question = ?', (question,))
            conn.commit()
            
if __name__ == '__main__':
    manager = DB_Manager('database.db') # Ваше название датабазы
    manager.create_tables() # Создание базы данных