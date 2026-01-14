from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)

import datetime
from ..enterprise.models import Enterprise
from django.core.exceptions import ValidationError


class Vehicle(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    year_of_manufacture = models.IntegerField(
        verbose_name="Год выпуска",
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(datetime.date.today().year),
        ],
    )
    mileage = models.IntegerField(verbose_name="Пробег", help_text="Пробег (км)")
    number = models.CharField(max_length=6, verbose_name="Госномер", unique=True)
    vin = models.CharField(
        max_length=17,
        verbose_name="VIN",
        validators=[MinLengthValidator(17)],
        unique=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    model = models.ForeignKey("Model", on_delete=models.RESTRICT, verbose_name="Модель")

    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.RESTRICT, null=True, verbose_name="Предприятие"
    )

    class Meta:
        verbose_name = "Транспортное средство"
        verbose_name_plural = "Транспортные средства"

    def __str__(self):
        res = f"{self.model.name} {self.number}"

        if self.enterprise:
            res += f" ({self.enterprise.name})"

        return res


class Model(models.Model):
    name = models.CharField(max_length=35, verbose_name="Наименование")

    TYPES = [
        ("PCR", "Легковой"),
        ("BUS", "Автобус"),
        ("LRR", "Грузовой"),
    ]

    type = models.CharField(max_length=3, choices=TYPES, verbose_name="Тип")

    number_of_seats = models.IntegerField(verbose_name="Количество посадочных мест")
    tank_capacity_l = models.IntegerField(
        verbose_name="Объем бака", help_text="Объем бака (л)"
    )
    load_capacity_kg = models.IntegerField(
        verbose_name="Грузоподъемность", help_text="Грузоподъемность (кг)"
    )

    def __str__(self):
        return self.name

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = "Модель"
        verbose_name_plural = "Модели"


class Driver(models.Model):
    first_name = models.CharField(max_length=35, verbose_name="Имя")
    last_name = models.CharField(max_length=35, verbose_name="Фамилия")
    TIN = models.CharField(max_length=12, verbose_name="ИНН", unique=True)

    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.RESTRICT, verbose_name="Предприятие"
    )

    vehicles = models.ManyToManyField(
        Vehicle,
        through="VehicleDriver",
        through_fields=("driver", "vehicle"),
        related_name="drivers",
    )

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}" 

    class Meta:
        verbose_name = "Водитель"
        verbose_name_plural = "Водители"

    def __str__(self):
        res = f"{self.first_name} {self.last_name}"

        if self.enterprise:
            res += f" ({self.enterprise.name})"

        return res


class VehicleDriver(models.Model):
    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.CASCADE, verbose_name="Предприятие"
    )

    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, verbose_name="Водитель"
    )
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, verbose_name="Машина"
    )
    active = models.BooleanField(default=False, verbose_name="Активен")

    class Meta:
        verbose_name = "Машина водителя"
        verbose_name_plural = "Машины и водители"
        unique_together = ("driver", "vehicle")

    def clean(self):
        if self.driver.enterprise != self.enterprise:
            raise ValidationError(
                {
                    "driver": ValidationError(
                        f'У водителя организация "{self.driver.enterprise}" вместо "{self.enterprise}"'
                    ),
                }
            )

        if self.vehicle.enterprise != self.enterprise:
            raise ValidationError(
                {
                    "vehicle": ValidationError(
                        f'У транспортного средства организация "{self.vehicle.enterprise}" вместо "{self.enterprise}"'
                    ),
                }
            )

        if not self.active:
            return

        vehicle_drivers = VehicleDriver.objects.filter(
            driver=self.driver, active=True
        ).exclude(id=self.id)[:1]

        if len(vehicle_drivers) > 0 and vehicle_drivers[0].vehicle != self.vehicle:
            raise ValidationError(
                {
                    "active": ValidationError(
                        f"У водителя уже установлено активным транспортное средство {vehicle_drivers[0].vehicle}"
                    ),
                }
            )

        vehicle_drivers = VehicleDriver.objects.filter(
            vehicle=self.vehicle, active=True
        ).exclude(id=self.id)[:1]

        if len(vehicle_drivers) > 0 and vehicle_drivers[0].driver != self.driver:
            raise ValidationError(
                {
                    "active": ValidationError(
                        f"У транспортного средства уже установлен активным водитель {vehicle_drivers[0].driver}"
                    ),
                }
            )
