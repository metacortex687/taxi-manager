from taxi_manager.raw_application.chat_bot.interfaces import (
    IChatBotClient,
    IChatReportService,
)
from taxi_manager.raw_application.users.interfaces import IUserService

from . import states


class ChatBotService:
    def __init__(
        self,
        chat_bot_client: IChatBotClient,
        user_service: IUserService,
        chat_report_sevice: IChatReportService,
    ):
        print(chat_bot_client)
        self.chatbot_client = chat_bot_client
        self.user_service = user_service
        self.chat_report_sevice = chat_report_sevice
        self.state_user = {}

    def start(self):
        for chat_user_id, text in self.chatbot_client.listen():
            if not self.state_user.get(chat_user_id):
                self.state_user[chat_user_id] = states.StartState(
                    states.StateContext(
                        chat_user_id=chat_user_id,
                        user_service=self.user_service,
                        chat_report_sevice=self.chat_report_sevice,
                    )
                )

            res = self.state_user[chat_user_id].handle(text)
            new_state, texts = res
            self.state_user[chat_user_id] = new_state

            for text in texts:
                self.chatbot_client.send(chat_user_id, text)
