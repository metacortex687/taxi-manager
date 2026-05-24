class IUserService:
    def chat_user_login(self, chat_user_id, login, password) -> bool:
        raise NotImplementedError

    def is_chat_user_login(self, chat_user_id) -> bool:
        raise NotImplementedError
    
    def get_django_user_id(self, chat_user_id) -> int:
        raise NotImplementedError
    
    def chat_user_logout(self, chat_user_id) -> bool:
        raise NotImplementedError
    
    def get_chat_user_id(self, django_user_id) -> int:
        raise NotImplementedError


    