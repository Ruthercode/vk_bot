import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from src.tools import *
from src import commands_description
from src import keyboards


import time
import random


# Спустя много дней
# Порос костылями код
# Рефакторинг ждёт


class VkBot:

    def __init__(self, token):
        self.__token = token
        self.__vk = vk_api.VkApi(token=token).get_api()
        self.command_handler = keyboards.Handler()

    @staticmethod
    def likes_from_bot(target_ids, album, token, count=50):
        """Bot send POST request for VK API (Method likes.add)
        for all user's photos received through the photos.get method
        :arg target_ids: list of id's
        :arg album: - wall,saved,profile
        :arg token: - Your bot's access token. Is need for do something with vk api
        :arg count: - How many photos require like
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
                    return "Ошибка добавления лайка"
                else:
                    print("Photo (id: {0}) was liked".format(photo['id']))

                time.sleep(8)
        return "ok"

    def send_message(self, message, send_id, keyboard=None):
        """:arg message: Text of the message.
           :arg send_id: Destination ID.
           :return: None"""
        random_number = random.randint(10000, 100000)
        self.__vk.messages.send(peer_id=send_id,
                                message=message,
                                random_id=random_number,
                                keyboard=keyboard)

    def __command_handler(self, event):
        message = event.text
        self.command_handler.take_command(message)
        return self.command_handler.compute_next_step()



    def start_longpoll(self):
        longpoll = VkLongPoll(vk_api.VkApi(token=self.__token))
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                message = self.__command_handler(event)
                print(message)
                keyboard = None
                if not self.command_handler.current_node.is_tool:
                    keyboard = self.command_handler.current_node.obj.return_buttons()
                    if keyboard:
                        keyboard = keyboard.get_keyboard()
                self.send_message(message,
                                  event.user_id,
                                  keyboard=keyboard)
