from threading import Thread

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from kafka.services import start_listener_kafka
from vk_bot.bot_client import VkChatBotClient
from vk_bot.services import start_vk_bot_service


class Command(BaseCommand):
    def handle(self, *args, **options):
        token = settings.VK_BOT_TOKEN
        if not token:
            raise ImproperlyConfigured("Не установлен VK_BOT_TOKEN")

        group_id = settings.VK_BOT_GROUP_ID
        if not group_id:
            raise ImproperlyConfigured("Не установлен VK_BOT_GROUP_ID")

        auth_api_url = settings.AUTH_API_URL
        if not auth_api_url:
            raise ImproperlyConfigured(
                "Не установлен AUTH_API_URL. Адрес сервиса авторизации."
            )

        kafka_bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        if not kafka_bootstrap_servers:
            raise ImproperlyConfigured(
                "Не установлен KAFKA_BOOTSTRAP_SERVERS. Адрес kafka."
            )

        print("Сервис запущен")

        vk_bot_client = VkChatBotClient(token, group_id)

        threads = (
            Thread(
                target=start_listener_kafka,
                args=(kafka_bootstrap_servers, vk_bot_client),
                name="kafka-listener",
                daemon=True,
            ),
            Thread(
                target=start_vk_bot_service,
                args=(vk_bot_client, token, group_id, auth_api_url),
                name="vk-bot",
                daemon=True,
            ),
        )

        for thread in threads:
            thread.start()

        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            pass

        print("Сервис остановлен")