from pprint import pprint
import requests
import json
from datetime import timedelta
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm
import random
# Токен ВК
token = ' '



# Класс для работы с API ВК
class VkUser :
    url = 'https://api.vk.com/method/'
    def __init__(self,token,version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_users(self,user_id=None):
        url =self.url + 'users.get'
        users_params = {'user_ids':user_id,
                  'fields': 'sex, bdate  '
                  }
        res = requests.get(url, params={**self.params, **users_params}).json()
        return res
        # pprint(res)


    def users_search_3(self,hometown=None,age_from=None,age_to=None, sex=None):
        url =self.url + 'users.search'
        users_params = {
            'count':1000,
            'hometown':hometown ,
            'sex': sex ,
            'sort':0,
            'age_from':age_from ,
            'age_to': age_to,

            'fields': 'country,city, sex , bdate , domain '
            }
        res = requests.get(url, params={**self.params, **users_params}).json()
        # Избавимся от вложенности , создадим список с параметрами пользователей :
        users_info_list_all = res['response']['items']
        # pprint(users_info_list_all)
        # Отфильтруем лишние города и закрытые профили :
        users_info_list = []
        for user in users_info_list_all :
            if 'city' in user and user['city']['title'] == hometown and user['is_closed'] is False :
                users_info_list.append(user)

        return users_info_list

    # Работаем с фотографиями . Запрос на photos.get

    # @sleep_and_retry
    # @limits(calls=2, period=timedelta(seconds=1).total_seconds())
    def get_best_photos_2 (self,user_id=None,count=100):
        ''' Функция возвращает список из 3-х самых популярных по лайкам
        фотографий со стены пользователя. Используем декораторы
        @sleep_and_retry и @limits(calls=2, period=timedelta(seconds=1).total_seconds()),
        ограничивающие количество запросов в секунду.
        В данном случае отправляем 2 запроса в 1 секунду
        '''
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': user_id ,
            'album_id': 'wall',
            'rev': 1 ,
            'extended': 1 ,
            'photo_sizes': 1,
            'count': count
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        # pprint(res)

        # Избавляемся от закрытых профилей и профилей без фотографий:
        if 'response' in res and res ["response"]["count"]>0:
            # pprint (res)

            # Находим фото максимального размера.
            # Вытягиваем в отдельный файл блок "items":
            fotos_items_list = res ["response"]["items"]
            # pprint(fotos_items_list)
            size_dict = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
            data_photos_list = []
            for data in fotos_items_list :
                likes = data['likes']['count']
                size_max=0
                for element in data['sizes']:
                    letter_size_foto = element['type']
                    # Проверка на наличии обозначения размера фото в контрольном словаре размеров:
                    if letter_size_foto in size_dict.keys():
                      # Ищем фото с максимальным размером , сохраняем соответствующую букву размера (letter_max_foto)
                        # и ссылку на фото максимального размера (url_foto)
                        if size_dict[letter_size_foto] > size_max:

                            size_max = size_dict[letter_size_foto]
                            url_foto = element['url']
                    else:
                         print(f'Ошибка. Размера "{letter_size_foto}" нет в контрольном списке размеров фотографий')

                # Сохраняем данные о выбранном фото в текущем словаре:
                element_dict={
                              'likes' :  likes ,
                              'url_foto':url_foto
                              }
                # Добавляем текущий словарь в общий список из словарей с данными о выбранных фото:
                data_photos_list.append(element_dict)
                # Сортируем список по количеству лайков :
                data_photos_list_sort = sorted(data_photos_list, key=lambda x: x['likes'],reverse= True)
                # print(len(data_photos_list_sort))
                # pprint(data_photos_list_sort)

                # Выбираем 3 фото с максимальным количеством лайков:
                best_photos_list = data_photos_list_sort[:3]

                # Вытаскиваем адреса фотографий :
                best_photos_list_url= []
                for photo in best_photos_list:
                    best_photos_list_url.append(photo['url_foto'])
            return best_photos_list_url






    def get_companion (self,hometown=None,age_from=None,age_to=None, sex=None):
        '''Функция получает на вход параметры поиска ,
         возвращает данные одного собеседника '''
        # Получаем расширенную информацию о пользователях :
        users_info_list = self.users_search_3(hometown, age_from, age_to, sex)
        # pprint(users_info_list)
        print(f'Получено {len(users_info_list)} анкет(ы,а) ')
        # Работаем с каждой анкетой индивидуально:
        # user_info = users_info_list.pop(0)
        start = 'да'
        while len(users_info_list):
            if start.lower() == 'да':
                # Рандомный выбор из списка с удалением
                # test_list = [6, 4, 8, 9, 10]
                # x = test_list.pop(random.randrange(len(test_list)))
                user_info = users_info_list.pop(random.randrange(len(users_info_list)))
                # user_info = users_info_list.pop(0)
                # pprint(user_info)
                user_dict = {}
                user_id = user_info['id']
                # Получаем 3 фотографии нужного пользователя
                photos_url_list = vk_client.get_best_photos_2(user_id=user_id)
                # pprint (photos_url_list)
                # Наполняем текущий словарь требуемыми значениями .
                if photos_url_list is not None:
                    user_dict['bdate'] = user_info['bdate']
                    user_dict['city'] = user_info['city']['title']
                    user_dict['domain'] = user_info['domain']
                    user_dict['photos_url_list'] = photos_url_list
                    user_dict['first_name'] = user_info['first_name']
                    user_dict['last_name'] = user_info['last_name']
                    user_dict['sex'] = user_info['sex']
                    user_dict['id'] = user_info['id']
                pprint(user_dict)
                # Сохранение изображений из списка ссылок
                count = 0
                for url in tqdm(photos_url_list):
                    count += 1
                    name = f'photo-{count}'
                    res = requests.get(url)
                    with open(f'Foto_user/{name}.jpg', 'wb') as file:
                        file.write(res.content)

                start = input('Для просмотра следующего элемента списка напишите "да" - ')
            else:
                print("Вы вышли из режима просмотра анкет")
                break
        else:
            print()
            print('Список обработанных анкет законился.\n'
                  'Введите новые параметры поиска')


# Работаем с ВК:

# Инициализируем объект класса VkUser :
vk_client = VkUser(token, '5.131')



