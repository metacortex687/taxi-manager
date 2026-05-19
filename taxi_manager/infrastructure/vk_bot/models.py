from django.contrib.auth import get_user_model
from django.db import models

class VkUser(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    vk_user_id = models.CharField(max_length=15, unique=True)

