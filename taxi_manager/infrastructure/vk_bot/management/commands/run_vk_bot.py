from django.core.management.base import BaseCommand

from django.conf import settings


from taxi_manager.infrastructure.vk_bot.bot import VkChatBot
from taxi_manager.infrastructure.vk_bot.repositories import VkBotUserRepository
from taxi_manager.infrastructure.vk_bot.services import VKUserService
from taxi_manager.raw_application.chat_bot.services import ChatBotService


class Command(BaseCommand):
    def handle(self, *args, **options):
        token = settings.VK_BOT_TOKEN
        group_id = settings.VK_BOT_GROUP_ID

        if not token or not group_id:
            print("не установлены VK_BOT_TOKEN или VK_BOT_GROUP_ID")
            return

        chat_bot = ChatBotService(
            chat_bot_client=VkChatBot(token, group_id),
            user_service=VKUserService(vk_bot_user_repository=VkBotUserRepository()),
        )

        chat_bot.start()
