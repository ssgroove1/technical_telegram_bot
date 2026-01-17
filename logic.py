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
                            name TEXT,
                            FOREIGN KEY(message_id) REFERENCES messages(message_id)
                        )''')
            conn.execute('''CREATE TABLE messages (
                            message_id INTEGER PRIMARY KEY,
                            category TEXT NOT NULL,
                            message TEXT NOT NULL
                        )''')
            
if __name__ == '__main__':
    manager = DB_Manager('database.db') # Ваше название датабазы
    manager.create_tables() # Создание базы данных