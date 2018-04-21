import telebot, requests, threading, asyncio, json, io, aiohttp, traceback, lang
from vk.exceptions import *
from vk import Session, API
from PIL import Image
from settings import SETTINGS

tg = telebot.TeleBot(SETTINGS.TOKEN)

loop = asyncio.get_event_loop()

async def upload_photo(encoded_image, upload_url):
    try:
        data = aiohttp.FormData()
        data.add_field('photo',
                       encoded_image,
                       filename='picture.png',
                       content_type='multipart/form-data')

        async with aiohttp.ClientSession() as sess:
            async with sess.post(upload_url, data=data) as resp:
                result = json.loads(await resp.text())

        data = dict(photo=result['photo'], hash=result['hash'], server=result['server'])
        return data
    except Exception:
        tg.send_message(chat_id='@vk2tl', text=traceback.format_exc())

def InitUsers(data):
    for i in data:
        try:
            threading.Thread(target=AddUserToListen, args=(i[0], i[1])).start()
        except Exception:
            tg.send_message(chat_id='@vk2tl', text=traceback.format_exc())
    print('Загрузка пользователей прошла успешно!')

def AddUserToListen(tl_id, access_key):
    try:
        session = Session(access_token=access_key)
        vk = API(session)
        key = vk.messages.getLongPollServer()['key']
        server = vk.messages.getLongPollServer()['server']
        ts = vk.messages.getLongPollServer()['ts']
        while True:
            try:
                r = requests.get('https://'+str(server)+'?act=a_check&key='+str(key)+'&ts='+str(ts)+'&wait=60&mode=2&version=2')
                ts = r.json()['ts']
                upd = r.json()['updates']
                for i in range(len(upd)):
                    if upd[i][0]==4 and upd[i][2]!=51 and upd[i][2]!=19 and upd[i][2]!=35 and upd[i][2]!=547 and upd[i][2]!=563:
                        user = vk.users.get(user_ids=upd[i][3],fields='sex')[0]
                        msg_text = str(upd[i][5])
                        tg.send_message(chat_id=tl_id, disable_web_page_preview=True, parse_mode='HTML', text=lang.ru.UserReceiveHeader(user)+'\n'+msg_text)
                        msg = vk.messages.getById(message_ids=upd[i][1])[1]
                        if msg.get('attachments') != None:
                            for a in msg['attachments']:
                                try:
                                    if a['type']=='photo':
                                        img = a['photo']['src_big']
                                        tg.send_photo(chat_id=tl_id, photo=img)
                                    elif a['type']=='audio':
                                        tg.send_audio(chat_id=tl_id, audio=a['audio']['url'])
                                    elif a['type']=='doc':
                                        tg.send_document(chat_id=tl_id, data=a['doc']['url'])
                                except:
                                    tg.send_message(parse_mode='HTML', chat_id=tl_id, text="{ Упс, <b>illegal</b> <i>content</i> подъехал (from <b>VK</b>2<b>TL</b>) }")
                                    tg.send_photo(chat_id=tl_id, photo='https://pp.userapi.com/c840238/v840238044/1224e/IqdKCxysOVQ.jpg')

            except Exception:
                tg.send_message(chat_id='@vk2tl', text=traceback.format_exc())
    except VkAPIError:
        tg.send_message(parse_mode='HTML', chat_id=tl_id, text=lang.ru.api_error)
    except Exception:
        tg.send_message(chat_id='@vk2tl', text=traceback.format_exc())

def SendMsg(tl_id, access_key, reciever_id, msg):
    session = Session(access_token=access_key)
    vk = API(session)
    try:
        vk.messages.send(user_id=int(reciever_id), message=msg)
    except:
        try:
            vk.messages.send(domain=reciever_id, message=msg)
        except Exception as e:
            tg.send_message(chat_id=tl_id, text='Вернитесь в меню и проверьте правильность введённого ID.')
            print(e)

def SendImg(tl_id, access_key, reciever_id, img):
    try:
        img = Image.open(io.BytesIO(img))
        buffer = io.BytesIO()
        img.save(buffer, format='png')
        buffer.seek(0)
        session = Session(access_token=access_key)
        vk = API(session)
        r = loop.run_until_complete(upload_photo(buffer, vk.photos.getMessagesUploadServer()['upload_url']))
        final_image = vk.photos.saveMessagesPhoto(photo=r['photo'], server=r['server'], hash=r['hash'])
        try:
            vk.messages.send(user_id=int(reciever_id), message='', attachment=final_image[0]['id'])
        except:
            try:
                vk.messages.send(domain=reciever_id, message='', attachment=final_image[0]['id'])
            except:
                tg.send_message(chat_id=tl_id, text='Вернитесь в меню и проверьте правильность введённого ID.')
    except Exception:
        tg.send_message(chat_id='@vk2tl', text=traceback.format_exc())

def SendDoc(access_key, reciever_id, doc):
    session = Session(access_token=access_key)
    vk = API(session)
    url = vk.docs.getUploadServer()['upload_url']
    r = requests.post(url, files={'file': doc})
    print(r.json())
    print(url)
