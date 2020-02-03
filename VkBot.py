import vk_api
import time


class ClosedPageException (Exception):
    pass


class VkBot:
    def __init__(self,token):
        self.token = token
        self.vk = vk_api.VkApi(token=token).get_api()

    def likes_add_for_person(self,targets,album):
        targets = self.vk.users.get(user_ids=targets)
        for target in targets:
            is_closed = target["is_closed"]
            try:
                if is_closed:
                    raise ClosedPageException
            except ClosedPageException:
                print("{0}'s page ( https://vk.com/{1} ) is closed. Bot has no access".format(target["first_name"],target["id"]))
                continue

            try:
                photos = self.vk.photos.get(owner_id=target['id'],
                                       album_id=album,
                                       rev=1,
                                       count=1000)
                photos = photos["items"]
            except vk_api.exceptions.ApiError:
                print("{0}'s ( https://vk.com/{1} ) album is closed. Bot has no access".format(target["first_name"],target["id"]))
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
