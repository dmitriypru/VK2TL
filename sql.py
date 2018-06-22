import sqlite3
import funcs, telebot, traceback
from settings import SETTINGS

bot = telebot.TeleBot(SETTINGS().TOKEN)

class SQL:

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def select_all(self):
        """ Получаем все строки """
        with self.connection:
            try:
                return self.cursor.execute('SELECT * FROM users').fetchall()
            except Exception:
                bot.send_message(chat_id='@vk2tl', text=traceback.format_exc())

    def get_data(self, tl_id):
        """ Получаем одну строку с номером tl_id """
        with self.connection:
            try:
                return self.cursor.execute('SELECT * FROM users WHERE tl_id = ?', [tl_id]).fetchall()[0]
            except Exception:
                bot.send_message(chat_id='@vk2tl', text=traceback.format_exc())

    def count_rows(self):
        """ Считаем количество строк """
        with self.connection:
            try:
                result = self.cursor.execute('SELECT * FROM users').fetchall()
                return len(result)
            except Exception:
                bot.send_message(chat_id='@vk2tl', text=traceback.format_exc())

    def add_user(self, tl_id, access_key):
        """ Добавляем нового пользователя """
        with self.connection:
            try:
                funcs.AddUserToListen(tl_id, access_key)
                return self.cursor.execute('INSERT INTO users (tl_id, access_key) VALUES (?,?)', (tl_id,access_key))
            except Exception:
                bot.send_message(chat_id='@vk2tl', text=traceback.format_exc())

    def set_status(self, tl_id, is_writing,reciever_id):
        """ Устанавливаем значение диалога """
        with self.connection:
            try:
                return self.cursor.execute('UPDATE users SET is_writing= ?, reciever_id= ? WHERE tl_id= ?', (is_writing, str(reciever_id), tl_id))
            except Exception:
                bot.send_message(chat_id='@vk2tl', text=traceback.format_exc())

    def set_sender(self, tl_id, last_sender):
        """ Устанавливаем значение последнего писавшего """
        with self.connection:
            try:
                return self.cursor.execute('UPDATE users SET last_sender= ? WHERE tl_id= ?', (last_sender, tl_id))
            except Exception:
                print('akmadwkdaadwkjladwklawjdkljkdalkjl')

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
