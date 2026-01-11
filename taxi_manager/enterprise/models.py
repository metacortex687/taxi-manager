from django.db import models

class Enterprise(models.Model):
    name = models.CharField(max_length=25, verbose_name="Наименование", unique=True)
    city = models.CharField(max_length=25, verbose_name="Город")

