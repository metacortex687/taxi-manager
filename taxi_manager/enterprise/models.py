from django.db import models

class Enterprise(models.Model):
    name = models.CharField(max_length=25, verbose_name="Наименование", unique=True)
    city = models.CharField(max_length=25, verbose_name="Город")


class Driver(models.Model):
    first_name = models.CharField(max_length=35, verbose_name="Имя")
    last_name = models.CharField(max_length=35, verbose_name="Фвмилия")
    TIN = models.CharField(max_length=12, verbose_name="ИНН", unique=True) 

    enterprise = models.ForeignKey(Enterprise, on_delete=models.RESTRICT)

