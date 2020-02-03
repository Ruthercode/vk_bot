import vk_api
import time
from vk_api.longpoll import VkLongPoll, VkEventType


class ClosedPageException(Exception):
    pass


class VkBot:

    def __init__(self, token):
        self.token = token
        self.session = vk_api.VkApi(token=token)
        self.vk = self.session.get_api()
        self.commands = {"лайкай": self.likes_add_for_person}

    def likes_add_for_person(self, targets, album):
        code = 0
        targets = self.vk.users.get(user_ids=targets)
        for target in targets:
            is_closed = target["is_closed"]
            try:
                if is_closed:
                    raise ClosedPageException
            except ClosedPageException:
                code = 1
                print("{0}'s page ( https://vk.com/{1} ) is closed. Bot has no access".format(target["first_name"],
                                                                                              target["id"]))
                continue

            try:
                photos = self.vk.photos.get(owner_id=target['id'],
                                            album_id=album,
                                            rev=1,
                                            count=1000)
                photos = photos["items"]
            except vk_api.exceptions.ApiError:
                code = 1
                print("{0}'s ( https://vk.com/{1} ) album is closed. Bot has no access".format(target["first_name"],
                                                                                               target["id"]))
                continue

            for photo in photos:
                try:
                    self.vk.likes.add(type="photo",
                                      owner_id=target['id'],
                                      item_id=photo['id'])
                except self.vk.api.exceptions.ApiError:
                    code = 1
                    print("Error")
                else:
                    print("Photo (id: {0}) was liked".format(photo['id']))
                time.sleep(2)
            return code

    def say(self, message, identificator, chat):
        if chat:
            self.vk.messages.send(chat_id=identificator,
                                  message=message)
        else:
            self.vk.messages.send(user_id=identificator,
                                  message=message)

    def start_longpoll(self):
        longpoll = VkLongPoll(self.session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                message = event.text.split()
                if message[0] in self.commands.keys():
                    command = message[0]
                    mood = message[-1]
                    targets = message[1:-1]
                    code = self.commands[command](targets, mood)
                    if code:
                        message = "Failed"
                    else:
                        message = "Success"
                    if event.from_user:  # Если написали в ЛС
                        self.say(message, event.user_id, 0)
                    elif event.from_chat:  # Если написали в Беседе
                        self.say(message, event.chat_id, 1)
