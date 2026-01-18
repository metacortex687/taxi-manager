from django.db import models
from .query_sets import EnterpriseQuerySet
from django.contrib.auth import get_user_model

User = get_user_model()


class Enterprise(models.Model):
    name = models.CharField(max_length=35, verbose_name="Наименование", unique=True)
    city = models.CharField(max_length=25, verbose_name="Город")

    objects = EnterpriseQuerySet.as_manager()
    
    manager_users = models.ManyToManyField(
        User,
        through="Manager",
        through_fields=("enterprise", "user"),
        related_name="managed_enterprises",
    )

    def __str__(self):
        return f"{self.name} ({self.city})"

    class Meta:
        verbose_name = "Предприятие"
        verbose_name_plural = "Предприятия"


class Manager(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, verbose_name="Пользователь"
    )
    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.RESTRICT, verbose_name="Предприятие"
    )

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"
        unique_together = ("user", "enterprise")
