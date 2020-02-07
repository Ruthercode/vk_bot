import vk_api
import time
import random
from src import schedule, weather
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
import asyncio

class ClosedPageException(Exception):
    pass

# Спустя много дней
# Порос костылями код
# Рефакторинг ждёт


class VkBot:

    def __init__(self, token):
        self.__token = token
        self.__vk = vk_api.VkApi(token=token).get_api()
        self.__commands = {"погода": weather.get_weather,
                           "расписание" : self.schedule }  # TODO: add new commands and fix old
        self.__groups = {}
        with open("src/groups.txt") as infile:  # TODO: пофиксить инициализацию групп (не через текстовик)
            pair = infile.read().split()
            for i in range(0, pair.__len__(), 2):
                self.__groups[pair[i].lower()] = pair[i + 1]

    @staticmethod
    def likes_from_bot(target_ids, album,token, count=1000):
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
                print("{0}'s page ( https://vk.com/{1} ) is closed. Bot has no access".format(target["first_name"],
                                                                                              target["id"]))
                continue

            try:
                photos = vk.photos.get(owner_id=target['id'],
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
                    vk.likes.add(type="photo",
                                        owner_id=target['id'],
                                        item_id=photo['id'])
                except vk.api.exceptions.ApiError:
                    print("Error")
                else:
                    print("Photo (id: {0}) was liked".format(photo['id']))

                time.sleep(2)

    async def send_message(self, message, send_id):
        """Send POST request for VK API (messages.send)
        :param message: Text of the message.
        :param send_id: Destination ID."""
        random_number = random.randint(10000, 100000)
        self.__vk.messages.send(peer_id=send_id,
                                message=message,
                                random_id=random_number)

    def __help(self):
        commands_description = {
            "Погода %город%": "Выдаёт информацию о текущей погоде. Можно указать страну",
            "Расписание %группа%" : "Расписание вашей группы на сегодняшний день",
            "Исходный код" : "Ссылка на исходный код бота"}
        # TODO: Переодически обновлять

        response = "Все команды начинаются с обращения Эрнест или Эрнесто. \n" \
                   "Список команд: \n"

        for key in commands_description.keys():
            response = response + key + ' - ' + commands_description[key] + '\n'

        return response


    async def schedule(self, message):
        if message.__len__() == 0:
            message = ["ктбо1-7"]
        group = message[0]
        t = datetime.now().isocalendar()
        resp = "Расписание группы " + group + " на {0}.{1}.{2} :\n".format(t[1], (t[2] * 7 + t[1]) // 30, t[0])
        origin = datetime(2020, 2, 10, 0, 0).isocalendar()
        if group not in self.__groups.keys():
            return "Группы не существует"
        group = self.__groups[group]
        week = t[1] - origin[1] + 1
        resp = resp + await schedule.get_schedule(group, week, t[2] + 1)
        return resp

    async def __command_handler(self, event):
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
            response = await self.__commands[message[0]](message[1:])
        elif message[0] == "помощь":
            response = self.__help()
        elif message.__len__() == 2 and message[0] == "исходный" and message[1] == "код":
            response = "https://github.com/Ruthercode/vk_bot"
        else:
            response = "Команда не распознана, используйте команду 'помощь', чтобы узнать список команд"

        if event.from_user:
            await self.send_message(response, event.user_id)
        elif event.from_chat:
            await self.send_message(response, 2000000000 + event.chat_id)

    def start_longpoll(self):
        longpoll = VkLongPoll(vk_api.VkApi(token=self.__token))

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                asyncio.run(self.__command_handler(event))
