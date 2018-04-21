auth_url = 'https://oauth.vk.com/authorize?client_id=3544010&scope=photos,video,pages,messages,docs,offline&response_type=token'
class ru:
    unknown_error = '| Неизвестная ошибка. Попробуйте позже, либо напишите о проблеме куда-нибудь (from <b>VK</b>2<b>TL</b>) |'
    unknown_file_type = '| Отправка файлов такого типа в <b>данный момент</b> не реализована. Приносим извинения. (from <b>VK</b>2<b>TL</b>) |'
    too_many_requests = '| Братан, обожди чутка, ибо ебаное АПИ ВК не позволяет много запросов делать, а загружать твоих братишек в БД нам пока впадлу. (from <b>VK</b>2<b>TL</b>)|'
    api_error= '| При использовании вашего <b>access_token</b> получена ошибка. Попробуйте ввести новый (from <b>VK</b>2<b>TL</b>) |'

    def UserWriteHeader(user):
        uid = user['uid']
        first_name = user['first_name']
        last_name = user['last_name']
        return('Вы пишите <a href="https://vk.com/id'+str(uid)+'">'+first_name+' '+last_name+'</a> (ID:<b>'+str(uid)+'</b>) :')

    def UserReceiveHeader(user):
        uid = user['uid']
        first_name = user['first_name']
        last_name = user['last_name']
        sex = user['sex']
        if sex != 1:
            return('<a href="https://vk.com/id'+str(uid)+'">'+first_name+' '+last_name+'</a> (ID:<b>'+str(uid)+'</b>) прислал сообщение:')
        else:
            return('<a href="https://vk.com/id'+str(uid)+'">'+first_name+' '+last_name+'</a> (ID:<b>'+str(uid)+'</b>) прислала сообщение:')
