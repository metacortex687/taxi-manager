import threading

from django.apps import AppConfig

from .bot import start_bot


class VkBotConfig(AppConfig):
    name = 'taxi_manager.infrastructure.vk_bot'

    def ready(self):
        is_not_started = threading.Thread(name="vk_bot").ident == None

        if is_not_started:
            threading.Thread(name="vk_bot",target=start_bot, daemon=True).start()

