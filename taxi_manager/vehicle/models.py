from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MaxValueValidator,
    MinValueValidator,
)

import datetime


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

    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'

