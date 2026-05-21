
class VkBotUserRepository:
    def __init__(self):
        from .models import VkUser
        self.VkUserModel = VkUser

    def is_authenticated(self, vk_user_id: str):
        return self.VkUserModel.objects.filter(vk_user_id=vk_user_id).exists()

    def set_authenticated(self, django_user, vk_user_id: str):
        self.VkUserModel.objects.filter(vk_user_id=vk_user_id).delete()
        self.VkUserModel.objects.create(user=django_user, vk_user_id=vk_user_id)

    def get_django_user_id(self, vk_user_id: str) -> int:
        vk_user = self.VkUserModel.objects.filter(vk_user_id=vk_user_id).first()

        if vk_user is None:
            return None

        return vk_user.user.id


