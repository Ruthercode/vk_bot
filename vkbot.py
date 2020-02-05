import vk_api
import time
import random
import requests
from vk_api.longpoll import VkLongPoll, VkEventType


class ClosedPageException(Exception):
    pass

def bound(num):
    tmp = num
    tmp -= tmp//1

    if tmp < 0.5:
        return int(num//1)
    else:
        return int(num//1 + 1)


class VkBot:

    def __init__(self, token):
        self.token = token
        self.vk = vk_api.VkApi(token=token).get_api()
        self.commands = {"погода": self.__get_weather,
                         "помощь": self.__help}  #TODO: add new commands and fix old

    def likes_from_bot(self, target_ids, album, count=1000):
        """Bot send POST request for VK API (Method likes.add)
        for all user's photos received through the photos.get method

        :param targets: list of id's
        :param album: - string
        :param count: - int <= 1000
        :returns None: """
        targets = self.vk.users.get(user_ids=target_ids)

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
                photos = self.vk.photos.get(owner_id=target['id'],
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
                    self.vk.likes.add(type="photo",
                                      owner_id=target['id'],
                                      item_id=photo['id'])
                except self.vk.api.exceptions.ApiError:
                    print("Error")
                else:
                    print("Photo (id: {0}) was liked".format(photo['id']))

                time.sleep(2)


    def send_message(self, message, send_id):
        """Send POST request for VK API (messages.send)
        :param message: Text of the message.
        :param send_id: Destination ID."""
        random_number = random.randint(10000, 100000)
        self.vk.messages.send(peer_id=send_id,
                              message=message,
                              random_id=random_number)

    def __get_weather(self, message):
        sity = "moscow"
        country = "ru"
        if message.__len__() > 0:
            sity = message[0]
        if message.__len__() > 1:
            country = message[1]
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

        weather = {'description': d_weather['weather'][0]['description'],
                   'temp': bound(d_weather['main']['temp']),
                   'feels_like': bound(d_weather['main']['feels_like']),
                   'wind_speed': bound(d_weather['wind']['speed']),
                   'wind_deg': d_weather['wind']['deg'],
                   'clouds': d_weather['clouds']['all']}

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
               'Облачность: {clouds}%'.format(sity=d_weather['name'] + ', ' + d_weather['sys']['country'],
                                              description=weather['description'],
                                              temp=weather['temp'],
                                              feels_like=weather['feels_like'],
                                              wind_deg=weather['wind_deg'],
                                              wind_speed=weather['wind_speed'],
                                              clouds=weather['clouds'])

    def __help(self, message):
        commands_description = {
            "Погода %город%": "Выдаёт информацию о текущей погоде. Можно указать страну"}
        #TODO: Переодически обновлять

        response = "Все команды начинаются с обращения Эрнест или Эрнесто. \n" \
                   "Список команд: \n"

        for key in commands_description.keys():
            response = response + key + ' - ' + commands_description[key] + '\n'

        return response

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
        elif message[0] in self.commands.keys():
            response = self.commands[message[0]](message[1:])
        else:
            response = "Команда не распознана, используйте команду 'помощь', чтобы узнать список команд"

        if event.from_user:
            self.send_message(response, event.user_id)
        elif event.from_chat:
            self.send_message(response, 2000000000 + event.chat_id)

    def start_longpoll(self):
        longpoll = VkLongPoll(vk_api.VkApi(token=self.token))

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                self.__command_handler(event)
