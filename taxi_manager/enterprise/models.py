from django.db import models
from ..vehicle.models import Vehicle

class Enterprise(models.Model):
    name = models.CharField(max_length=25, verbose_name="Наименование", unique=True)
    city = models.CharField(max_length=25, verbose_name="Город")


class Driver(models.Model):
    first_name = models.CharField(max_length=35, verbose_name="Имя")
    last_name = models.CharField(max_length=35, verbose_name="Фвмилия")
    TIN = models.CharField(max_length=12, verbose_name="ИНН", unique=True) 

    enterprise = models.ForeignKey(Enterprise, on_delete=models.RESTRICT)

    vehicles = models.ManyToManyField(Vehicle, through="VehicleDriver", through_fields=("driver", "vehicle"), related_name='drivers')


class VehicleDriver(models.Model):
    driver  = models.ForeignKey(Driver, on_delete=models.CASCADE) 
    vehicle = models.ForeignKey(Driver, on_delete=models.CASCADE)    



