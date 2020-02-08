import vk_api
import time
import random
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
import requests


class ClosedPageException(Exception):
    pass


# Спустя много дней
# Порос костылями код
# Рефакторинг ждёт

# ----------------------------------------------------------------------------------------------------------------------
class ResponseHandler:
    template = ''

    def clean_response(self, response):
        pass

    def return_template(self, response):
        response = self.clean_response(response)
        if type(response) == type({}):
            return self.template.format(**response)
        elif type(response) == type([]) or type(response) == type(()):
            return self.template.format(*response)
        else:
            return self.template.format(response)


class ScheduleResponseHandler(ResponseHandler):
    def __init__(self, day):
        self.template = "1-я 08:00-09:35) {0}\n" \
                        "2-я 09:50-11:25) {1}\n" \
                        "3-я 11:55-13:30) {2}\n" \
                        "4-я 13:45-15:20) {3}\n" \
                        "5-я 15:50-17:25) {4}\n" \
                        "6-я 17:40-19:15) {5}\n" \
                        "7-я 19:30-21:05) {6}"
        self.day = day

    def clean_response(self, response):
        if response.__len__() == 0:
            self.template = "Группы не существует или вы пытаетесь узнать расписание на неучебный день"
            return {}
        if self.day == 7:
            self.template = "Воскресенье - не учебный день. Можете отдохнуть"
            return {}
        response = response['table']['table'][self.day]
        response.pop(0)
        return response


class SearchResponseHandler(ResponseHandler):
    def __init__(self):
        self.template = '{}'

    def clean_response(self, response):
        if response['response']['items'].__len__():
            response = int(response['response']['items'][0]['id'])
        else:
            response = -1
        return response


class WeatherResponseHandler(ResponseHandler):
    def __init__(self):
        self.template = '— {description} \n' \
                        '— Температура: {temp}\n' \
                        '— Ощущается как {feels_like} \n' \
                        '— Ветер {wind}, cкорость {wind_speed}м/с  \n' \
                        '— Облачность: {clouds}% \n' \
                        '— Влажность: {humidity}%'

    def clean_response(self, response):
        if response['meta']['code'] != '200':
            self.template = "Ошибка определения города. Погода не определена"
            return {}
        response = response['response']

        wind_scale_8 = {0: 'Штиль',
                        1: 'Северный',
                        2: 'Северо-восточный',
                        3: 'Восточный',
                        4: 'Юго-восточный',
                        5: 'Южный',
                        6: 'Юго-западный',
                        7: 'Западный',
                        8: 'Северо-западный',
                        None: "Отсутствует"}

        resp = dict(description=response['description']['full'],
                    temp=response['temperature']['air']['C'],
                    feels_like=response['temperature']['comfort']['C'],
                    wind=wind_scale_8[response['wind']['direction']['scale_8']],
                    wind_speed=response['wind']['speed']['m_s'],
                    clouds=response['cloudiness']['percent'],
                    humidity=response['humidity']['percent'])
        return resp


# ----------------------------------------------------------------------------------------------------------------------
class Tool:
    url = ''
    response_handler = ''
    params = {}

    def GET_request(self):
        response = requests.get(url=self.url, params=self.params)
        if response.status_code == 200:
            return response.json()
        else:
            return {}

    def set_response_handler(self):
        raise AttributeError('Not Implemented ResponseHandler')

    def get_response(self):
        return self.response_handler.return_template(self.GET_request())


class ScheduleTool(Tool):
    def __init__(self, group="ктбо1-7"):
        self.url = "http://165.22.28.187/schedule-api/"
        with open("src/groups.txt") as file:
            for line in file:
                pair = line.lower().split()
                if group == pair[0]:
                    group = pair[1]
                    break
        self.params = {"group": group,
                       "week": datetime.now().isocalendar()[1] - datetime(2020, 2, 10, 0, 0).isocalendar()[1] + 1}

    def set_response_handler(self):
        self.response_handler = ScheduleResponseHandler(datetime.now().isocalendar()[2])


class SearchTool(Tool):
    def __init__(self, sity='таганрог'):
        self.url = 'https://api.gismeteo.net/v2/search/cities/'
        self.params = dict(query=sity)

    def GET_request(self):
        response = requests.get(url=self.url,
                                params=self.params,
                                headers={'X-Gismeteo-Token': '5c51afc32bfd12.13951840',
                                         'Accept-Encoding': 'deflate,gzip'})
        return response.json()

    def set_response_handler(self):
        self.response_handler = SearchResponseHandler()


class WeatherTool(Tool):
    def __init__(self, id):
        self.url = 'https://api.gismeteo.net/v2/weather/current/' + str(id) + '/'
        self.params = {'X-Gismeteo-Token': '5c51afc32bfd12.13951840',
                       'Accept-Encoding': 'deflate,gzip'}

    def GET_request(self):
        response = requests.get(url=self.url, headers=self.params)
        return response.json()

    def set_response_handler(self):
        self.response_handler = WeatherResponseHandler()


# ----------------------------------------------------------------------------------------------------------------------

# def singleton(cls):
#     instances = {}
#
#     def get_instance():
#         if cls not in instances:
#             instances[cls] = cls()
#         return instances[cls]
#
#     return get_instance


class VkBot:

    def __init__(self, token):
        self.__token = token
        self.__vk = vk_api.VkApi(token=token).get_api()

    @staticmethod
    def likes_from_bot(target_ids, album, token, count=1000):
        """Bot send POST request for VK API (Method likes.add)
        for all user's photos received through the photos.get method

        :param targets: list of id's
        :param album: - string
        :param count: - int <= 1000
        :returns None: """

        vk = vk_api.VkApi(token=token).get_api()
        targets = vk.users.get(user_ids=target_ids)

        for target in targets:

            is_closed = target["is_closed"]
            try:
                if is_closed:
                    raise ClosedPageException
            except ClosedPageException:
                return "{0}'s page ( https://vk.com/{1} ) is closed. Bot has no access".format(target["first_name"],
                                                                                               target["id"])

            try:
                photos = vk.photos.get(owner_id=target['id'],
                                       album_id=album,
                                       count=count,
                                       rev=1)
                photos = photos["items"]
            except vk_api.exceptions.ApiError:
                return "{0}'s ( https://vk.com/{1} ) album is closed. Bot has no access".format(target["first_name"],
                                                                                                target["id"])

            for photo in photos:
                try:
                    vk.likes.add(type="photo",
                                 owner_id=target['id'],
                                 item_id=photo['id'])
                except vk.api.exceptions.ApiError:
                    return "Error"
                else:
                    print("Photo (id: {0}) was liked".format(photo['id']))

                time.sleep(2)
        return "ok"

    def send_message(self, message, send_id):
        """Send POST request for VK API (messages.send)
        :param message: Text of the message.
        :param send_id: Destination ID."""
        random_number = random.randint(10000, 100000)
        self.__vk.messages.send(peer_id=send_id,
                                message=message,
                                random_id=random_number)

    def __command_handler(self, event):
        message = event.text.lower().translate(str.maketrans("", "", ".,?!")).split()

        try:
            if message[0][:6] != "эрнест":
                return
        except IndexError:
            return

        message.pop(0)
        if message.__len__() == 0:
            response = "Да-да я"
        elif message[0] == "погода":
            message.pop(0)
            if message.__len__() == 0:
                tool = SearchTool()
            else:
                tool = SearchTool(' '.join(message))

            tool.set_response_handler()
            tool = WeatherTool(tool.get_response())
            tool.set_response_handler()
            response = tool.get_response()
        elif message[0] == "расписание":
            message.pop(0)
            if message.__len__() == 0:
                tool = ScheduleTool()
            else:
                tool = ScheduleTool(' '.join(message))
            tool.set_response_handler()
            response = tool.get_response()
        elif message[0] == "лайки":
            message.pop(0)
            try:
                response = VkBot.likes_from_bot(target_ids=message[:1], album="profile", token=self.__token)
            except Exception:
                response = "Выполнение команды невозможно"
        elif message[0] == "помощь":
            commands_description = {
                "Погода %город%": "Выдаёт информацию о текущей погоде. Можно указать страну",
                "Расписание %группа%": "Расписание вашей группы на сегодняшний день",
                "Исходный код": "Ссылка на исходный код бота",
                "Лайки %ссылка%": "Бот лайкает все фото профиля указанного id"}
            # TODO: Переодически обновлять

            response = "Все команды начинаются с обращения Эрнест или Эрнесто. \n" \
                       "Список команд: \n"
            for key in commands_description.keys():
                response = response + '------------------------------------\n'
                response = response + key + ' - ' + commands_description[key] + '\n' \
 \
        elif message.__len__() == 2 and message[0] == "исходный" and message[1] == "код":
            response = "https://github.com/Ruthercode/vk_bot"
        else:
            response = "Команда не распознана, используйте команду 'помощь', чтобы узнать список команд"

        if event.from_user:
            self.send_message(response, event.user_id)
        elif event.from_chat:
            self.send_message(response, 2000000000 + event.chat_id)

    def start_longpoll(self):
        longpoll = VkLongPoll(vk_api.VkApi(token=self.__token))

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                self.__command_handler(event)