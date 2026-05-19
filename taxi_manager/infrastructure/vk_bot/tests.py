from django.test import TestCase

from django.contrib.auth import authenticate, get_user_model

from taxi_manager.infrastructure.vk_bot.repositories import VkBotUserRepository
from taxi_manager.infrastructure.vk_bot.services import VKUserService

class VehicleAPITest(TestCase):
    def setUp(self):
        self.username = "user"
        self.password = "secret"
        self.vk_chat_user_id = "12345"
        self.user = get_user_model().objects.create_user(
            username=self.username , email="test@mail.com", password=self.password
        )

    def test_authenticate(self):
        vk_user_service = VKUserService(vk_bot_user_repository = VkBotUserRepository())

        result = vk_user_service.chat_user_login(self.vk_chat_user_id, self.username, self.password)
        self.assertTrue(result)

        result = vk_user_service.is_chat_user_login(self.vk_chat_user_id)
        self.assertTrue(result)

        result = vk_user_service.is_chat_user_login("123123")
        self.assertFalse(result)

        user = authenticate(username=self.username , password=self.password)
        self.assertIsNotNone(user)
