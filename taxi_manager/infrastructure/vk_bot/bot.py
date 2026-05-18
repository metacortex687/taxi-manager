import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from django.conf import settings



def write_message(obj_vk_api, sender, message):
    obj_vk_api.method('messages.send', {'peer_id': sender, 'message': message, 'random_id': get_random_id()})



def start_bot():
    token = settings.VK_BOT_TOKEN
    group_id = settings.VK_BOT_GROUP_ID

    if not token or not group_id:
        print("не установлены VK_BOT_TOKEN или VK_BOT_GROUP_ID")
        return 

    obj_vk_api = vk_api.VkApi(token=token)

    obj_vk_api.method("groups.getLongPollServer",values={"group_id": group_id})
    longpol = VkBotLongPoll(obj_vk_api,group_id=group_id)


    print("VK_BOT запущен")

    for event in longpol.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:

            reseived_massage = event.message.text
            sender = event.message.from_id

            write_message(obj_vk_api, sender, reseived_massage)