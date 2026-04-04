from django.contrib.gis.db import models

from taxi_manager.vehicle.models import Vehicle
from taxi_manager.enterprise.models import Enterprise

class VehicleLocationQuerySet(models.QuerySet):
    def filter_period(self, period_from, period_to):        
        return self.filter(tracked_at__gte=period_from, tracked_at__lt=period_to)
    
    def filter_enterprise(self, enterprise):
        return self.filter(enterprise=enterprise)


class VehicleLocation(models.Model):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.RESTRICT,
        verbose_name="Предприятие",
        related_name="locations",
        null=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.RESTRICT,
        related_name="locations",
        verbose_name="Автомобиль",
    )
    location = models.PointField(
        srid=4326, geography=True
    )  # 4326 идентификатор системы координат для GPS
    tracked_at = models.DateTimeField()

    objects = VehicleLocationQuerySet.as_manager()


class Trip(models.Model):
    enterprise = models.ForeignKey(
        Enterprise, on_delete=models.RESTRICT, verbose_name="Предприятие", related_name="trips"
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.RESTRICT,
        related_name="trips",
        verbose_name="Автомобиль",
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
