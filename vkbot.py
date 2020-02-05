import vk_api
import time
import random
import requests
import schedule
from datetime import datetime, time
from vk_api.longpoll import VkLongPoll, VkEventType


class ClosedPageException(Exception):
    pass


def get_weather(message):
    sity = "taganrog"
    country = "ru"
    if message.__len__() > 0:
        sity = message[:-1]
    if message.__len__() > 1:
        country = ' '.join(message[-1:])
    url = 'http://api.openweathermap.org/data/2.5/find'

    params = dict(
        q=sity + ',' + country,
        APPID='2266edad3793720bbd46eea84c35fcfb',
        units='metric',
        lang='ru'
    )

    resp = requests.get(url=url, params=params)
    d_weather = resp.json()

    print(d_weather)

    if d_weather['cod'] == '404':
        return "Город не найден"

    bound = lambda num: num % 1 > 0.5 and int(num + 1) or int(num)

    weather = {'description': d_weather["list"][0]['weather'][0]['description'],
               'temp': bound(d_weather["list"][0]['main']['temp']),
               'feels_like': bound(d_weather["list"][0]['main']['feels_like']),
               'wind_speed': bound(d_weather["list"][0]['wind']['speed']),
               'wind_deg': d_weather["list"][0]['wind']['deg'],
               'clouds': d_weather["list"][0]['clouds']['all']}

    wind_vector = ""
    if 180 > weather['wind_deg'] > 0:
        wind_vector = wind_vector + "С"
    elif 360 > weather['wind_deg'] > 180:
        wind_vector = wind_vector + "Ю"

    if 270 > weather['wind_deg'] > 90:
        wind_vector = wind_vector + "З"
    elif weather['wind_deg'] != 90 and weather['wind_deg'] != 270:
        wind_vector = wind_vector + "В"
    weather['wind_deg'] = wind_vector

    return 'В городе {sity} сейчас {description} \n' \
           'Температура: {temp}\n' \
           'Ощущается как {feels_like} \n' \
           'Ветер {wind_deg}, cкорость {wind_speed}мс  \n' \
           'Облачность: {clouds}%'.format(sity=d_weather["list"][0]['name'] + ', ' + d_weather["list"][0]['sys']['country'],
                                          description=weather['description'],
                                          temp=weather['temp'],
                                          feels_like=weather['feels_like'],
                                          wind_deg=weather['wind_deg'],
                                          wind_speed=weather['wind_speed'],
                                          clouds=weather['clouds'])


class VkBot:

    def __init__(self, token):
        self.__token = token
        self.__vk = vk_api.VkApi(token=token).get_api()
        self.__commands = {"погода": get_weather,
                           "помощь": self.__help,
                           "расписание" : self.schedule }  # TODO: add new commands and fix old
        self.__groups = {}
        with open("groups.txt") as infile:  # TODO: пофиксить инициализацию групп (не через текстовик)
            pair = infile.read().split()
            for i in range(0, pair.__len__(), 2):
                self.__groups[pair[i].lower()] = pair[i + 1]

    def likes_from_bot(self, target_ids, album, count=1000):
        """Bot send POST request for VK API (Method likes.add)
        for all user's photos received through the photos.get method

        :param targets: list of id's
        :param album: - string
        :param count: - int <= 1000
        :returns None: """
        targets = self.__vk.users.get(user_ids=target_ids)

        for target in targets:

            is_closed = target["is_closed"]
            try:
                if is_closed:
                    raise ClosedPageException
            except ClosedPageException:
                print("{0}'s page ( https://vk.com/{1} ) is closed. Bot has no access".format(target["first_name"],
                                                                                              target["id"]))
                continue

            try:
                photos = self.__vk.photos.get(owner_id=target['id'],
                                              album_id=album,
                                              rev=1,
                                              count=count)
                photos = photos["items"]
            except vk_api.exceptions.ApiError:
                print("{0}'s ( https://vk.com/{1} ) album is closed. Bot has no access".format(target["first_name"],
                                                                                               target["id"]))
                continue

            for photo in photos:
                try:
                    self.__vk.likes.add(type="photo",
                                        owner_id=target['id'],
                                        item_id=photo['id'])
                except self.__vk.api.exceptions.ApiError:
                    print("Error")
                else:
                    print("Photo (id: {0}) was liked".format(photo['id']))

                time.sleep(2)

    def send_message(self, message, send_id):
        """Send POST request for VK API (messages.send)
        :param message: Text of the message.
        :param send_id: Destination ID."""
        random_number = random.randint(10000, 100000)
        self.__vk.messages.send(peer_id=send_id,
                                message=message,
                                random_id=random_number)

    def __help(self, message):
        commands_description = {
            "Погода %город%": "Выдаёт информацию о текущей погоде. Можно указать страну",
            "Расписание %группа%" : "Расписание вашей группы на сегодняшний день"}
        # TODO: Переодически обновлять

        response = "Все команды начинаются с обращения Эрнест или Эрнесто. \n" \
                   "Список команд: \n"

        for key in commands_description.keys():
            response = response + key + ' - ' + commands_description[key] + '\n'

        return response

    def schedule(self, message):
        if message.__len__() == 0:
            message = ["ктбо1-7"]
        group = message[0]
        resp = "Расписание группы " + group + " на сегоднящний день:\n"
        origin = datetime(2020, 2, 3, 0, 0).isocalendar()
        if group not in self.__groups.keys():
            return "Группы не существует"
        group = self.__groups[group]
        t = datetime.now().isocalendar()
        week = t[1] - origin[1] + 1
        resp = resp + schedule.get_schedule(group, week, t[2] + 1)
        return resp

    def __command_handler(self, event):
        message = event.text.lower().translate(str.maketrans("", "", ".,?!")).split()

        call = message[0]
        if call.__len__() < 6:
            return
        elif call[:6] != "эрнест":
            return

        message = message[1:]
        if message.__len__() == 0:
            response = "Да да я"
        elif message[0] in self.__commands.keys():
            response = self.__commands[message[0]](message[1:])
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
