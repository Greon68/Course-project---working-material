from random import randrange
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload
from tqdm import tqdm
from pprint import pprint
import random
from vk_api.keyboard import  VkKeyboard , VkKeyboardColor


# Токен сообщества для чат-бота:
token_group = ' '
# token_group = input('Token: ')




vk_bot = vk_api.VkApi(token=token_group) # АВТОРИЗАТОР ( сессия )
longpoll = VkLongPoll(vk_bot) # Переменная для работы с API типа LongPoll

# Переменная - загрузчик изображений
uploader = VkUpload(vk_bot)

# СОЗДАНИЕ КЛАВИАТУРЫ (КНОПОК)
# Создадим переменную , содержащую вызов клавитатуры:
# one_time= True - одноразовая клавиаиура
# one_time= False - многоразовая клавиатура
keyboard = VkKeyboard(one_time= True)
# Пропишем кнопки :
keyboard.add_button('Начать',color=VkKeyboardColor.POSITIVE)
# keyboard.add_line() # делает кнопку на всю ширину поля сообщения
keyboard.add_button('Новый поиск', color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_button('Фото', color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
# Кнопка для перехода по ссылке
keyboard.add_openlink_button('Кнопка со ссылкой', link = 'https://vk.com')

# адрес изображения для загрузки
image = 'D:/ФОТО/good_day.jpg'
image_list = ['Foto/photo-0.jpg','Foto/photo-1.jpg','Foto/photo-2.jpg','Foto/photo-3.jpg' ]
perplexity_photo_list = ['удивление.jpg','не_понимаю.jpeg','не_понимаю-2.jpg']




def write_msg(user_id, message=None ,attachment=None):
    '''Функция для отправки сообщения'''
    vk_bot.method('messages.send',
                  {'user_id': user_id,
                   'message': message,
                   'attachment':attachment,
                   'keyboard': keyboard.get_keyboard(),
                   'random_id': randrange(10 ** 7)})


def upload_image(photos,user_id, message=None ):
    '''Функция отправки изображений.
    Здесь : photos - путь к фотографии на локальном компьютере,
     message- текст сообщения (не обязательный параметр)'''
    # Загрузчик фотографий.
    # Результат запроса - список со словарём внутри
    # Избавляемся от списка , оставляем словарь
    upload_dict= uploader.photo_messages(photos)[0]
    # pprint(upload_dict)
    # Вытаскиваем из словаря необходимые параметры
    owner_id = upload_dict["owner_id"]
    media_id = upload_dict["id"]
    # Аргумент для загрузки фото:
    attachment = f'photo{owner_id}_{media_id}'
    print(f'Параметры загруженного изображения - {attachment}') # photo-221946829_456239071
    # Загружаем изображение с помощью функции write_msg()
    write_msg(user_id, message, attachment)

def get_user_name(user_id):
    '''Получаем имя пользователя по его id ,
     используя метод users.get '''
    user_name_list = vk_bot.method('users.get',{'user_ids':user_id , 'fields': 'first_name' })
    # pprint(user_name_list)
    user_name = user_name_list[0]['first_name']
    return user_name

def random_number():
    number = random.randint(0,10)
    return number

def random_number_2(message):
    end = int(message)
    number = random.randint(0,end+1)
    return number

def chatbot():
    # Функция longpoll.listen() 'слушает' сервер ВКонтакте ,
    # event - сообщение , пришедшее на сервер (== в чат группы )
    # Используем прогресс-бар tqdm для контроля работы кода
    for event in tqdm(longpoll.listen()):
        # Сравниваем тип пришедшего сообщения с тем , что мы ожидаем ,
        # есть ли такой тип в библиотеке vk_api, а , именно , в её подразделе VkEventType ,
        # т.е. проверяем соответствует ли полученное событие шаблонам события получения сообщений
        # Проверяем , кому именно адресовано событие ( сообщение ) -
        # действительно ли сообщение адресовано нашему боту
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            # Проверяем , кому именно адресовано событие ( сообщение ) -
            # действительно ли сообщение адресовано нашему боту
            messages_input = event.text
            print()
            print(f'Сообщение от пользователя - {messages_input}')
            # Запишем в переменную идентификатор собеседника :
            user_id = event.user_id
            print(f'user_id - {user_id}')

            # Опрелелим  имя пользователя по его user_id ,
            # вызвав метод get_name_user() класса VkUser
            # name_user = vk_client.get_name_user(user_id)
            name_user = get_user_name(user_id)

            if  messages_input.lower() == "начать" :
                upload_image('чат-бот.png', user_id,f'Привет, {name_user}! Я - Чат-Бот. Буду рад пообщаться !!!')
                write_msg(user_id,' Если хочешь , чтобы я подобрал для тебя собеседников , '
                                  'пришли сообщение со словом "старт" или  нажми кнопку "Новый поиск" :\n'
                                  '1 - получение случайного числа ;\n'
                                  '2 - вводим 4 требуемых параметра', attachment=None)
            elif messages_input.lower() == "привет" :
                upload_image(image, user_id,f"Привет, {name_user}! ")

            elif messages_input.lower() == "пока":
                # write_msg(user_id, f"Пока, {name_user}. Заходи ещё !")
                upload_image('пока.jpg', user_id, f"До свидания, {name_user}!")

            elif messages_input.lower() == "фото":
                for img in image_list:
                        upload_image(img,user_id,"Фото для Вас !" )

            # Подучение случайного числа :
            elif messages_input =='1':
                # write_msg(user_id=user_id,message= random_number())
                write_msg(user_id=user_id,message="Диапозон чисел от 0 до ...")
                # Снова слушаем чат :
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        msg = event.text # То , что получили от пользователя
                        user_id = event.user_id
                        # Проверяем , является ли полученное сообщение - числом :
                        try:
                            msg = int(msg)
                            write_msg(user_id=user_id, message=random_number_2(msg))
                            # break
                        except:
                            write_msg(user_id=user_id, message="Введено не число")
                            break


            # Получение набора параметров в диалоге от пользователя:
            # НЕ РАБОТАЕТ - НЕ ВЫХОДИТ ИЗ ЦИКЛА
            elif messages_input == '2':
                write_msg(user_id=user_id,message="Введите название города")
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        sity = event.text # Название города
                        write_msg(user_id=user_id, message="Введите пол собеседника (м/ж)")
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                sex = event.text.lower() # Пол собеседника

                                write_msg(user_id=user_id, message="Введите нижнюю границу возраста")
                                for event in longpoll.listen():
                                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                        age_from = event.text  # Нижняя граница возраста

                                        write_msg(user_id=user_id, message="Введите верхнюю границу возраста")
                                        for event in longpoll.listen():
                                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                                age_to = event.text  # Нижняя граница возраста
                                                user_id = event.user_id
                                                try:
                                                    age_to = int(age_to)
                                                    write_msg(user_id=user_id, message=f"Вы ввели следующие данные: \n"
                                                     f"Город - {sity} , пол собеседника - {sex}, возраст : от {age_from} до {age_to} лет ")
                                                    # break
                                                except:
                                                    write_msg(user_id=user_id, message="Введено не число")
                                                # print(sity,sex,age_from,age_to)
                                                    break



            else:
                # write_msg(user_id, "Не понял Ваш вопрос...")
                # Рандомная загрузка фото из списка :
                upload_image(random.choice(perplexity_photo_list), user_id, "Не понял Ваш вопрос...")

# Запускаю в работу :
chatbot()

