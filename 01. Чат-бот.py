from random import randrange
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload
from tqdm import tqdm
from pprint import pprint
import random



# token = input('Token: ')
token = ''


# Класс для работы с API ВК
class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_users(self, user_id=None):
        ''' Функция возвращает данные пользователя по его id'''
        url = self.url + 'users.get'
        users_params = {
            'user_id': user_id,
            'fields': 'education,city_name, sex,has_photo,photo_max_orig'
        }
        res = requests.get(url, params={**self.params, **users_params}).json()
        return res
        # pprint(res)



    def get_name_user(self,user_id=None):
        ''' Функция возвращает имя пользователя по его id '''
        self.user_id = user_id
        data_json = self.get_users(user_id)
        name_user = data_json['response'][0]['first_name']
        return name_user
        # print(name_user)





vk_client = VkUser(token, '5.131')



# адрес изображения для загрузки
image = 'good_day.jpg'
image_list = ['Foto/photo-0.jpg','Foto/photo-1.jpg','Foto/photo-2.jpg','Foto/photo-3.jpg' ]
perplexity_photo_list = ['удивление.jpg','не_понимаю.jpeg','не_понимаю-2.jpg']

authorize = vk_api.VkApi(token=token) # АВТОРИЗАТОР ( сессия )
longpoll = VkLongPoll(authorize) # Переменная для работы с API типа LongPoll
# Переменная - загрузчик изображений
uploader = VkUpload(authorize)


def write_msg(user_id, message=None ,attachment=None):
    '''Функция для отправки сообщения'''
    authorize.method('messages.send', {'user_id': user_id, 'message': message,'attachment':attachment, 'random_id': randrange(10 ** 7)})
    # authorize.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'attachment':attachment})

def upload_image(photos,user_id, message=None ):
    '''Функция отправки изображений.
    Здесь : photos - путь к фотографии на локальном компьютере,
     message- текст сообщения (не обязательный параметр)
     Внутри себя вызывает функцию отправки сообщений write_msg()'''
    # Загрузчик фотографий.
    # Результат запроса - список со словарём внутри
    # Избавляемся от списка , оставляем словарь
    upload_dict = uploader.photo_messages(photos)[0]
    pprint(upload_dict) # Для проверки
    # Вытаскиваем из словаря необходимые параметры
    owner_id = upload_dict["owner_id"]
    media_id = upload_dict["id"]
    # Аргумент для загрузки фото:
    attachment = f'photo{owner_id}_{media_id}'
    print(attachment) # photo-221946829_456239071
    # Загружаем изображение с помощью функции write_msg()
    write_msg(user_id, message, attachment)

# Функция longpoll.listen() 'слушает' сервер ВКонтакте ,
# event - сообщение , пришедшее на сервер (== в чат группы )
# Используем прогресс-бар tqdm для контроля работы кода
for event in tqdm(longpoll.listen()):
    # Сравниваем тип пришедшего сообщения с тем , что мы ожидаем ,
    # есть ли такой тип в библиотеке vk_api, а , именно , в её подразделе VkEventType ,
    # т.е. проверяем соответствует ли полученное событие шаблонам события получения сообщений
    if event.type == VkEventType.MESSAGE_NEW :
        # Проверяем , кому именно адресовано событие ( сообщение ) -
        # действительно ли сообщение адресовано нашему боту
        if event.to_me:
            # Проверяем , является ли полученнное сообщение текстом ( функция event.text),
            # и полученный текст сохраняем в переменную request :
            messages_input = event.text
            # Запишем в переменную идентификатор собеседника :
            user_id = event.user_id

            # Опрелелим  имя пользователя по его user_id ,
            # вызвав метод get_name_user() класса VkUser
            name_user = vk_client.get_name_user(user_id)

            # Диалоги
            if  messages_input.lower() == "начать" :
                upload_image('чат-бот.png', user_id,f'Привет, {name_user}! Я - Чат-Бот. Буду рад пообщаться !!!')
                write_msg(user_id,'Я умею реагировать на слова "привет" , "пока" и на любые другие сообщения .\n'                                 
                                  'Захочешь получить несколько красивых фотографий , напиши слово "фото".\n'
                                  ' Если хочешь , чтобы я подобрал для тебя собеседников , пришли сообщение со словом "старт" ', attachment=None)
            elif messages_input.lower() == "привет" :
                upload_image(image, user_id,f"Привет, {name_user}! ")
            elif messages_input.lower() == "пока":
                upload_image('пока.jpg', user_id, f"До свидания, {name_user}!")
            elif messages_input.lower() == "фото":
                for img in image_list:
                    upload_image(img,user_id,"Фото для Вас !" )
            else:
                # Рандомная загрузка фото из списка :
                upload_image(random.choice(perplexity_photo_list), user_id, "Не понял Ваш вопрос...")



