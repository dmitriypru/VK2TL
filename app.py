import telebot, requests, threading, funcs, sys, lang
from reply_keyboard_markups import Keyboard
from sql import SQL
from vk import Session, API, exceptions
from settings import SETTINGS

tg = telebot.TeleBot(SETTINGS.TOKEN)

db = SQL(SETTINGS.DB_NAME)
keyboard = Keyboard(tg)
funcs.InitUsers(db.select_all())

@tg.message_handler(commands=['menu'])
def BackToMenu(message):
    try:
        db.set_status(message.chat.id, 0, "")
        keyboard.main_menu(message)
    except Exception:
        tg.send_message(parse_mode='HTML', chat_id=message.chat.id, text=lang.ru.unknown_error)
        print(sys.exc_info())
        pass

@tg.message_handler(func=lambda a: 'Вернуться в меню' == a.text, content_types=['text'])
def GoToMenu(message):
    try:
        db.set_status(message.chat.id, 0, "")
        keyboard.main_menu(message)
    except Exception:
        tg.send_message(parse_mode='HTML', chat_id=message.chat.id, text=lang.ru.unknown_error)
        print(sys.exc_info())
        pass

@tg.message_handler(func=lambda a: 'Написать другу' == a.text, content_types=['text'])
def MsgToFriend(message):
    try:
        tg.send_message(chat_id=message.chat.id, text='Выберите друга:', reply_markup=keyboard.friends_menu(db.get_data(int(message.chat.id))))
    except Exception:
        tg.send_message(parse_mode='HTML', chat_id=message.chat.id, text=lang.ru.unknown_error)
        print(sys.exc_info())
        pass

@tg.message_handler(func=lambda a: 'Написать по ID' == a.text, content_types=['text'])
def MsgById(message):
    try:
        db.set_status(message.chat.id, 1, "")
        tg.send_message(chat_id=message.chat.id, text="Введите ID или домен пользователя:")
    except Exception as e:
        tg.send_message(parse_mode='HTML', chat_id=message.chat.id, text=lang.ru.unknown_error)
        print(sys.exc_info())
        print(e)
        pass

@tg.callback_query_handler(func=lambda call: True)
def CallbackChecker(call):
    try:
        vk = API(Session(db.get_data(call.message.chat.id)[1]))
        if call.data[:15] == 'write_to_friend':
            reciever_id = int(call.data[16:])
            db.set_status(call.from_user.id, 2, reciever_id)
            user = vk.users.get(user_ids = reciever_id, name_case = 'dat')[0]
            tg.delete_message(message_id=call.message.message_id, chat_id=call.message.chat.id)
            tg.send_message(reply_markup=keyboard.in_conversation(), parse_mode='HTML', chat_id=call.message.chat.id, disable_web_page_preview=True, text=lang.ru.UserWriteHeader(user))
        if call.data[:6] == 'topage':
            if int(call.data[7:]) != 0:
                tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = 'Выберите друга:',reply_markup = keyboard.other_friends(db.get_data(int(call.message.chat.id)),str(int(call.data[7:]))))
            else:
                tg.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = 'Выберите друга:', reply_markup=keyboard.friends_menu(db.get_data(int(call.message.chat.id))))
    except:
        print(sys.exc_info())
        pass

@tg.message_handler(content_types=['text', 'audio', 'document', 'photo', 'sticker'])
def MsgSorter(message):
    try:
        data = db.get_data(message.chat.id)
        vk = API(Session(data[1]))
        if data[2]==2:
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
        elif data[2]==1:
            db.set_status(message.chat.id, 2, message.text)
            user = vk.users.get(user_ids = message.text, name_case = 'dat')[0]
            tg.send_message(reply_markup=keyboard.in_conversation(), parse_mode='HTML', chat_id=message.chat.id, disable_web_page_preview=True, text=lang.ru.UserWriteHeader(user))
    except:
        print(sys.exc_info())
        pass

if __name__=="__main__":
    tg.polling()
