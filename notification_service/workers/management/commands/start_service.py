from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand

from vk_bot.services import start_vk_bot_service


class Command(BaseCommand):
    def handle(self, *args, **options):

        token = settings.VK_BOT_TOKEN
        if not token:
            raise ImproperlyConfigured("Не установлен VK_BOT_TOKEN")

        group_id = settings.VK_BOT_GROUP_ID
        if not group_id:
            raise ImproperlyConfigured("Не установлен VK_BOT_GROUP_ID")  

        print("Сервис запущен")

        start_vk_bot_service(token, group_id)

        print("Сервис остановлен")
