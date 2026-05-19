from taxi_manager.raw_application.users.interfaces import IUserService


class VKUserService(IUserService):
    def __init__(self):
        self.is_login = False

    def chat_user_login(self, chat_user_id, login, password):
        self.is_login = True
        print(chat_user_id, login, password)
        return self.is_chat_user_login(chat_user_id)
    
    def is_chat_user_login(self, chat_user_id):
        return self.is_login
