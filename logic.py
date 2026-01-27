import sqlite3

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            message_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            username TEXT,
                            first_name TEXT,
                            FOREIGN KEY(message_id) REFERENCES messages(message_id)
                        )''')
            conn.execute('''CREATE TABLE messages (
                            message_id INTEGER PRIMARY KEY,
                            status TEXT NOT NULL,
                            category TEXT NOT NULL,
                            message TEXT NOT NULL
                        )''')
            conn.execute('''CREATE TABLE questions (
                            count INTEGER PRIMARY KEY
                            user_id INTEGER,
                            category TEXT,
                            question TEXT,
                            answer TEXT
                        )''')
            
    def get_question(self, category):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor() 
            cur.execute('SELECT question FROM questions WHERE category = ?', (category,))
            return cur.fetchall()
        
    def get_answer(self, question):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor() 
            cur.execute('SELECT answer FROM questions WHERE question = ?', (question,))
            return cur.fetchall()[0]
            
if __name__ == '__main__':
    manager = DB_Manager('database.db') # Ваше название датабазы
   # manager.create_tables() # Создание базы данных
    print(manager.get_question("Заказ"))