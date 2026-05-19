from taxi_manager.raw_application.chat_bot.interfaces import IChatBotClient
from taxi_manager.raw_application.users.interfaces import IUserService


class ChatBotService:
    def __init__(self, chat_bot_client: IChatBotClient, user_service: IUserService):
        self.chatbot_client = chat_bot_client
        self.user_service = user_service

    def start(self):
        for chat_user_id, text in self.chatbot_client.listen():

            if text.startswith("/login"):
                self.authorization(text, chat_user_id)
                continue

            if not self.user_service.is_chat_user_login(chat_user_id):
                self.chatbot_client.send(
                    chat_user_id, "Авторизуйтесь: /login username password"
                )
                continue

            self.chatbot_client.send(chat_user_id, f"Чат бот: {text}")

    def authorization(self, text: str, chat_user_id):
        text = text.replace("/login","")
        text = text.strip()
        username, password = text.split()

        if self.user_service.chat_user_login(chat_user_id, username, password):
            self.chatbot_client.send(
                chat_user_id, f"Вы успешно авторизоавались: {username}"
            )
            return

        self.chatbot_client.send(chat_user_id, "Неверное имя пользователя или логин")
