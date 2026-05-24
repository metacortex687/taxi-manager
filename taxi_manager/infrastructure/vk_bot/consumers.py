from django.conf import settings

from django_pgwatch.consumer import BaseConsumer, NotificationHandler

from taxi_manager.infrastructure.enterprise.reposipories import EnterpriseRepository
from taxi_manager.infrastructure.geo_tracking.models import Trip
from taxi_manager.infrastructure.vk_bot.bot import VkChatBotClient
from taxi_manager.infrastructure.vk_bot.repositories import VkBotUserRepository
from taxi_manager.infrastructure.vk_bot.services import VKUserService
from taxi_manager.raw_application.chat_bot.services import ChatBotNotificationService


class VkBotTripChangeConsumer(BaseConsumer):
    consumer_id = "vk_bot_trip_change"
    channels = ["data_change"]

    def __init__(self, consumer_id = None, channels = None, timeout_seconds = 30, reconnect_delay = 5, max_batch_size = 100, max_workers = 4):
        token = settings.VK_BOT_TOKEN
        group_id = settings.VK_BOT_GROUP_ID

        if not token or not group_id:
            print("Не установлены токен или группа для VK-бота") 


        self.notification_service = ChatBotNotificationService(
            chat_bot_client=VkChatBotClient(token, group_id),
            user_service=VKUserService(vk_bot_user_repository=VkBotUserRepository()),
            enterprise_repository=EnterpriseRepository()
            ) 


        super().__init__(consumer_id, channels, timeout_seconds, reconnect_delay, max_batch_size, max_workers)

    def handle_notification(self, handler: NotificationHandler):
        if handler.get_table() != Trip._meta.db_table:
            return

        if handler.is_insert():
            self.notification_service.on_save_trip(handler.get_new_data())
            # print("Создана поездка:", handler.get_new_data())

        # elif handler.is_update():
        #     print("Поездка изменена:", handler.get_old_data(), "->", handler.get_new_data())

        # elif handler.is_delete():
        #     print("Поездка удалена:", handler.get_old_data())