import telebot
from telebot.types import KeyboardButton as btn
from telebot.types import InlineKeyboardButton as createBtn
from vk import Session, API
from lang import auth_url
from time import sleep
from math import ceil, floor

class Keyboard:
    def __init__(self, bot):
        self.bot = bot

    def force_main_menu(self):
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Написать другу')
        keyboard.row('Написать по ID')
        keyboard.row('Настройки')
        return keyboard

    def main_menu(self, message):
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Написать другу')
        keyboard.row('Написать по ID')
        keyboard.row('Настройки')
        self.bot.send_message(chat_id=message.chat.id, text='Выберите пункт в меню :', reply_markup=keyboard)

    def friends_menu(self, data):
        print(data, flush=True)
        access_key = data[1]
        vk = API(Session(access_token=access_key))
        friends = vk.friends.get(order='hints', count=5,v='5.74')['items']
        users = []
        keyboard = telebot.types.InlineKeyboardMarkup()
        userbtn = []
        for i in friends:
            temp_user = vk.users.get(user_ids=i,v='5.74')[0]
            users.append((temp_user['first_name'] + ' ' + temp_user['last_name'],temp_user['id']))
            userbtn.append(createBtn(text=users[friends.index(i)][0],callback_data='write_to_friend '+str(i)))
        userbtn.append(createBtn(text='>>',callback_data='topage_1'))
        keyboard.row(userbtn[0])
        keyboard.row(userbtn[1],userbtn[2])
        keyboard.row(userbtn[3],userbtn[4])
        keyboard.row(userbtn[5])
        return keyboard

    def other_friends(self, data, page):
        page = int(page)
        access_key = data[1]
        vk = API(Session(access_token=access_key))
        friends = vk.friends.get(order='hints', count=(page*6)+5,v='5.74')['items']
        friends = friends[(((page-1)*6)+5):]
        users = []
        userbtn = []
        keyboard = telebot.types.InlineKeyboardMarkup()

        for i in friends:
            temp_user = vk.users.get(user_ids=i,v='5.74')[0]
            users.append((temp_user['first_name'] + ' ' + temp_user['last_name'],temp_user['id']))
            userbtn.append(createBtn(text=users[friends.index(i)][0],callback_data='write_to_friend '+str(i)))
            sleep(0.4)
        for i in range(floor(len(friends)/2)):
            keyboard.row(userbtn[2*i],userbtn[2*i+1])
        if len(friends) % 2 == 1:
            keyboard.row(userbtn[len(friends)-1])
            keyboard.row(createBtn(text='<<', callback_data='topage_'+str(page-1)))
        else:
            keyboard.row(createBtn(text='<<', callback_data='topage_'+str(page-1)),createBtn(text='>>', callback_data='topage_'+str(page+1)))

        return keyboard

    def authorization(self,message_id):
        keyboard = telebot.types.InlineKeyboardMarkup()
        url_button = telebot.types.InlineKeyboardButton(text="Перейти на форму авторизации", url=auth_url)
        keyboard.add(url_button)

        return keyboard

    def in_conversation(self):
        keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        keyboard.row('Вернуться в меню')
        return keyboard
