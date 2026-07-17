import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


class VkChatBotClient():
    def __init__(self, token, group_id):
        self.token = token
        self.group_id = group_id
        self.obj_vk_api = None
        
        self.obj_vk_api = vk_api.VkApi(token=self.token)

        self.obj_vk_api.method(
            "groups.getLongPollServer", values={"group_id": self.group_id}
        )
        self.longpol = VkBotLongPoll(self.obj_vk_api, group_id=self.group_id)

    def listen(self):
        print("VK_BOT запущен")

        for event in self.longpol.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                reseived_massage = event.message.text
                sender = event.message.from_id

                yield (sender, reseived_massage)

                # write_message(obj_vk_api, sender, reseived_massage)

    def send(self, chat_user_id, message):
        self.obj_vk_api.method(
            "messages.send",
            {"peer_id": chat_user_id, "message": message, "random_id": get_random_id()},
        )
