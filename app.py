import telebot, requests, threading, funcs, sys, lang
from reply_keyboard_markups import Keyboard
from sql import SQL
from vk import Session, API, exceptions
from settings import SETTINGS

"""
Proxy Settings
Use only HTTP/HTTPS proxies (not socks5)
"""
telebot.apihelper.proxy = {'https':'https://80.211.141.177:8888'}

""" Bot and keyboard initialization """
tg = telebot.TeleBot(SETTINGS().TOKEN)
keyboard = Keyboard(tg)

""" Database initialization """
db = SQL(SETTINGS().DB_NAME)

""" Authorized users initialization from sqlite3 DB """
funcs.InitUsers(db.select_all())

@tg.message_handler(func=lambda message: 'Вернуться в меню' == message.text or '/menu' == message.text, content_types=['text'])
def BackToMenu(message):
    """
    'menu' command handler

    Return: user to main menu and makes user status and last sender default
    """
    db.set_status(message.chat.id, 0, "")
    db.set_sender(message.chat.id, 0)
    keyboard.main_menu(message)

@tg.message_handler(commands=['who'])
def CurrentReciever(message):
    """
    'who' command handler

    Return: name of current chat-user
    """
    reciever_id = db.get_data(message.chat.id)[3]
    if reciever_id != "":
        vk = API(Session(db.get_data(message.chat.id)[1]))
        user = vk.users.get(user_ids = reciever_id, name_case = 'dat',v='5.74')[0]
        tg.send_message(chat_id=message.chat.id, disable_web_page_preview=True, text=lang.ru.UserWriteHeader(user), parse_mode='HTML')
    else:
        tg.send_message(chat_id=message.chat.id, text='Собеседник не выбран.', parse_mode='HTML')

@tg.message_handler(func=lambda message: 'Написать другу' == message.text, content_types=['text'])
def MsgToFriend(message):
    """
    'write to friend' command handler

    Return: friends list
    """
    tg.send_message(chat_id=message.chat.id, text='Выберите друга:', reply_markup=keyboard.friends_menu(db.get_data(int(message.chat.id))))
    db.set_sender(message.chat.id, 0)

@tg.message_handler(func=lambda message: 'Написать по ID' == message.text, content_types=['text'])
def MsgById(message):
    """
    'write by id' command handler

    Return: Waiting for message from user with ChatID
    """
    tg.send_message(chat_id=message.chat.id, text='Введите ID:')
    db.set_status(message.chat.id, 1, "")
    db.set_sender(message.chat.id, 0) #Turn On message handler

@tg.message_handler(func=lambda message: 'Настройки' == message.text, content_types=['text'])
def Settings(message):
    """
    'settings' command handler

    ***not realized yet***
    """
    tg.send_message(chat_id=message.chat.id, text='Введите ID:')
    db.set_sender(message.chat.id, 0) # On message handler


#Inline callback checker
@tg.callback_query_handler(func=lambda call: True)
def CallbackChecker(call):
    """
    Inline callback checker

    Sorts user requests by additional data and makes useful things
    """
    db.set_sender(call.message.chat.id, 0)
    vk = API(Session(db.get_data(call.message.chat.id)[1]))
    if call.data[:15] == 'write_to_friend':
        reciever_id = int(call.data[16:])
        db.set_status(call.from_user.id, 2, reciever_id)
        user = vk.users.get(user_ids = reciever_id, name_case = 'dat',v='5.74')[0]
        tg.delete_message(message_id=call.message.message_id, chat_id=call.message.chat.id)
        tg.send_message(reply_markup=keyboard.in_conversation(), parse_mode='HTML', chat_id=call.message.chat.id, disable_web_page_preview=True, text=lang.ru.UserWriteHeader(user))
    if call.data[:6] == 'topage':
        if int(call.data[7:]) != 0:
            tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = 'Выберите друга:',reply_markup = keyboard.other_friends(db.get_data(int(call.message.chat.id)),str(int(call.data[7:]))))
        else:
            tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = 'Выберите друга:', reply_markup=keyboard.friends_menu(db.get_data(int(call.message.chat.id))))

@tg.message_handler(content_types=['text', 'audio', 'document', 'photo', 'sticker'])
def MsgSorter(message):
    """
    Handler of additional data (like a media, documents, stickers, etc)

    Return: nothing
    """
    data = db.get_data(message.chat.id)
    vk = API(Session(data[1]))
    if data[2]==2: # 2 - user write by link. Reciver ID stored in DB.
        usr = db.get_data(message.chat.id)
        if message.content_type=='text':
            funcs.SendMsg(usr[0], usr[1], usr[3], message.text)
        elif message.content_type=='photo':
            path = tg.get_file(file_id=message.photo[2].file_id).file_path
            img = tg.download_file(file_path=path)
            funcs.SendImg(usr[0], usr[1], usr[3], img)
        elif message.content_type=='sticker':
            path = tg.get_file(file_id=message.sticker.file_id).file_path
            img = tg.download_file(file_path=path)
            funcs.SendImg(usr[0], usr[1], usr[3], img)
        else:
            tg.send_message(parse_mode='HTML', chat_id=message.chat.id, text=lang.ru.unknown_file_type)
    elif data[2]==1: # 1 - user write by ID. We get reciver ID by message.
        db.set_status(message.chat.id, 2, message.text)
        user = vk.users.get(user_ids = message.text, name_case = 'dat',v='5.74')[0]
        tg.send_message(reply_markup=keyboard.in_conversation(), parse_mode='HTML', chat_id=message.chat.id, disable_web_page_preview=True, text=lang.ru.UserWriteHeader(user))


if __name__=="__main__":
    tg.polling()
