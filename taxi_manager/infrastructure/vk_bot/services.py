from django.contrib.auth import authenticate

from taxi_manager.infrastructure.vk_bot.repositories import VkBotUserRepository
from taxi_manager.raw_application.users.interfaces import IUserService


class VKUserService(IUserService):
    def __init__(self, vk_bot_user_repository: VkBotUserRepository):
        self.vk_bot_user_repository = vk_bot_user_repository

    def chat_user_login(self, chat_user_id, login, password):
        user = authenticate(username=login, password=password)
        if user is not None:
            self.vk_bot_user_repository.set_authenticated(user, chat_user_id)

        return self.is_chat_user_login(chat_user_id)

    def is_chat_user_login(self, chat_user_id):
        return self.vk_bot_user_repository.is_authenticated(chat_user_id)
    
    def get_django_user_id(self, chat_user_id) -> int:
        return self.vk_bot_user_repository.get_django_user_id(chat_user_id)
    
    def get_chat_user_id(self, django_user_id) -> int:
        return self.vk_bot_user_repository.get_chat_user_id(django_user_id)

    def chat_user_logout(self, chat_user_id) -> bool:
        return self.vk_bot_user_repository.logout(chat_user_id)