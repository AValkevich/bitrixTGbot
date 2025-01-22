import sqlite3

class Database:
    def __init__(self, db_name='bot.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            bitrix_id TEXT
        )
        ''')
        self.conn.commit()

    def get_user_id(self, chat_id):
        self.cursor.execute('SELECT user_id FROM users WHERE chat_id = ?', (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_bitrix_id(self, chat_id):
        self.cursor.execute('SELECT bitrix_id FROM users WHERE chat_id = ?', (chat_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def save_user_id(self, chat_id, user_id):
        self.cursor.execute('INSERT OR REPLACE INTO users (chat_id, user_id) VALUES (?, ?)', (chat_id, user_id))
        self.conn.commit()

    def save_bitrix_id(self, chat_id, bitrix_id):
        # Проверяем, существует ли запись с таким chat_id
        self.cursor.execute('SELECT user_id FROM users WHERE chat_id = ?', (chat_id,))
        result = self.cursor.fetchone()
        if result:
            # Если запись существует, обновляем bitrix_id
            self.cursor.execute('UPDATE users SET bitrix_id = ? WHERE chat_id = ?', (bitrix_id, chat_id))
        else:
            # Если записи нет, создаем новую запись с user_id по умолчанию
            self.cursor.execute('INSERT INTO users (chat_id, user_id, bitrix_id) VALUES (?, ?, ?)', (chat_id, "default_user_id", bitrix_id))
        self.conn.commit()

    def close(self):
        self.conn.close()