from django.db import models

class VkAccount(models.Model):
    user_uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        verbose_name="UUID пользователя taxi_manager",
    )

    chat_user_id = models.BigIntegerField(
        unique=True,
        verbose_name="Идентификатор пользователя чата",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата привязки",
    )

    class Meta:
        verbose_name = "Привязка учётной записи"
        verbose_name_plural = "Привязки учётных записей"

    

