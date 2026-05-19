import threading

from django.apps import AppConfig
from django.conf import settings


from taxi_manager.infrastructure.vk_bot.repositories import VkBotUserRepository
from taxi_manager.infrastructure.vk_bot.services import VKUserService
from taxi_manager.raw_application.chat_bot.services import ChatBotService

from .bot import VkChatBot


class VkBotConfig(AppConfig):
    name = 'taxi_manager.infrastructure.vk_bot'

    def ready(self):
        is_not_started = threading.Thread(name="vk_bot").ident == None

        if is_not_started:
            token = settings.VK_BOT_TOKEN
            group_id = settings.VK_BOT_GROUP_ID

            if not token or not group_id:
                print("не установлены VK_BOT_TOKEN или VK_BOT_GROUP_ID")
                return 
            
            chat_bot = ChatBotService(
                chat_bot_client = VkChatBot(token, group_id),
                user_service =  VKUserService(vk_bot_user_repository = VkBotUserRepository())
            )

            threading.Thread(name="vk_bot",target=chat_bot.start, daemon=True).start()

