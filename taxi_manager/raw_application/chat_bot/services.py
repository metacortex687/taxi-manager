from datetime import datetime

from taxi_manager.raw_application.chat_bot.interfaces import (
    IChatBotClient,
    IChatReportService,
    IEnterpriseRepository,
    IVehicleRepository,
)
from taxi_manager.raw_application.users.interfaces import IUserService

from zoneinfo import ZoneInfo

from . import states


class ChatBotService:
    def __init__(
        self,
        chat_bot_client: IChatBotClient,
        user_service: IUserService,
        chat_report_sevice: IChatReportService,
    ):
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


class ChatBotNotificationService:
    def __init__(
        self,
        chat_bot_client: IChatBotClient,
        user_service: IUserService,
        enterprise_repository: IEnterpriseRepository,
        vehicle_repository: IVehicleRepository,
    ):
        self.chatbot_client = chat_bot_client
        self.user_service = user_service
        self.enterprise_repository = enterprise_repository
        self.vehicle_repository = vehicle_repository

    def on_save_trip(self, trip_dict):
        
        print(trip_dict)

        manager_ids = self.enterprise_repository.assigment_manager_ids(
            trip_dict["enterprise_id"]
        )

        for manager_id in manager_ids:
            chat_user_id = self.user_service.get_chat_user_id(manager_id)
            if not chat_user_id:
                continue

            enterprise_id = trip_dict["enterprise_id"]
            enterprise_info = self.enterprise_repository.enterprises_info_dict(
                [enterprise_id]
            )[enterprise_id]

            enterprise_name = enterprise_info["name"]
            time_zone = enterprise_info["time_zone"]

            started_at = datetime.fromisoformat(trip_dict["started_at"]).astimezone(
                time_zone
            ).strftime("%y.%m %H:%M")
            ended_at = datetime.fromisoformat(trip_dict["ended_at"]).astimezone(
                time_zone
            ).strftime("%y.%m %H:%M")

            car_info = self.vehicle_repository.get_by_id(trip_dict["vehicle_id"])

            car_number = car_info["number"]

            message = (
                f"Новая поездка по предприятию {enterprise_name}:\n"
                f"Период {started_at}-{ended_at} (временная зона {time_zone});\n"
                f"Автомобиль: {car_number};\n"
            )

            self.chatbot_client.send(chat_user_id, message)
