from taxi_manager.raw_application.chat_bot.interfaces import IChatReportService
from taxi_manager.raw_application.users.interfaces import IUserService



class IState:
    def handle(text: str) -> tuple["IState", list[str]]:
        raise NotImplementedError


class StateContext:
    def __init__(self, chat_user_id, user_service: IUserService, chat_report_sevice:  IChatReportService):
        self.chat_user_id = chat_user_id
        self.user_service = user_service
        self.chat_report_sevice = chat_report_sevice


class StartState(IState):
    def __init__(self, state_context: StateContext):
        self.state_context = state_context
        self.chat_user_id = self.state_context.chat_user_id
        self.user_service = self.state_context.user_service
        self.chat_report_sevice = self.state_context.chat_report_sevice

    def handle(self, text: str):
        if text.startswith("/login"):
            new_state, text = self.authorization(text, self.chat_user_id)
            return new_state, text

        if not self.user_service.is_chat_user_login(self.chat_user_id):
            return self, ["Авторизуйтесь: /login username password"]
        
        return AuthorizedState(self.state_context).handle(text)

    def authorization(self, text: str, chat_user_id):
        text = text.replace("/login", "")
        text = text.strip()
        username, password = text.split()

        if self.user_service.chat_user_login(chat_user_id, username, password):
            return AuthorizedState(self.state_context), [
                f"Вы успешно авторизоавались: {username}"
            ]+["Список отчетов:"]+self.chat_report_sevice.list_reports()

        return self, ["Неверное имя пользователя или логин"]


class AuthorizedState(IState):
    def __init__(self, state_context: StateContext):
        self.state_context = state_context
        self.chat_user_id = self.state_context.chat_user_id
        self.chat_report_sevice = self.state_context.chat_report_sevice
        self.user_service = self.state_context.user_service
              

    def handle(self, text):
        if text.startswith("/report"):
            django_user_id = self.user_service.get_django_user_id(self.chat_user_id)
            return self, self.chat_report_sevice.report(text.replace("/report", "").strip(), django_user_id) 
        
        return self, ["Список отчетов:"]+self.chat_report_sevice.list_reports() 

