from django.contrib.gis.db import models
from django.db.models import F, OuterRef, Subquery, Value
from django.db.models.functions import Cast

from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.db.models.aggregates import MakeLine
from django.contrib.gis.db.models.functions import Length

from taxi_manager.infrastructure.vehicle.models import Vehicle
from taxi_manager.infrastructure.enterprise.models import Enterprise


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

class STAsGeoJSON(models.Func):
    function = "ST_AsGeoJSON"
    output_field = models.TextField()


class JsonbBuildObject(models.Func):
    function = "jsonb_build_object"
    output_field = models.JSONField()

class TripQuerySet(models.QuerySet):
    def filter_period(self, period_from, period_to):
        return self.filter(started_at__gte=period_from, ended_at__lt=period_to)

    def filter_enterprise(self, enterprise):
        return self.filter(enterprise=enterprise)

    def filter_vehicle(self, vehicle):
        return self.filter(vehicle=vehicle)

    def filter_vehicles(self, vehicle_ids):
        return self.filter(vehicle__in=vehicle_ids)

    def annotate_path(self):
        path_subquery = (
            VehicleLocation.objects.filter(
                vehicle=OuterRef("vehicle"),
                tracked_at__gte=OuterRef("started_at"),
                tracked_at__lt=OuterRef("ended_at"),
            )
            .order_by()
            .values("vehicle")
            .annotate(
                path=MakeLine(Cast("location", output_field=GeometryField(srid=4326)))
            )
            .values("path")[:1]
        )

        return self.annotate(
            path=Subquery(
                path_subquery,
                output_field=GeometryField(srid=4326),
            )
        )

   
    def annotate_geojson_feature(self):
        route_geojson_subquery = (
            VehicleLocation.objects.filter(
                vehicle=OuterRef("vehicle"),
                tracked_at__gte=OuterRef("started_at"),
                tracked_at__lt=OuterRef("ended_at"),
            )
            .order_by()
            .values("vehicle")
            .annotate(
                route_geojson=Cast(
                    STAsGeoJSON(
                        MakeLine(
                            Cast(
                                "location",
                                output_field=GeometryField(srid=4326),
                            )
                        )
                    ),
                    output_field=models.JSONField(),
                )
            )
            .values("route_geojson")[:1]
        )

        return (
            self.annotate(
                route_geojson=Subquery(
                    route_geojson_subquery,
                    output_field=models.JSONField(),
                )
            )
            .annotate(
                geojson_feature=JsonbBuildObject(
                    Value("type"),
                    Value("Feature"),
                    Value("geometry"),
                    F("route_geojson"),
                    Value("properties"),
                    JsonbBuildObject(
                        Value("trip"),
                        F("id"),
                    ),
                )
            )
        )

    def annotate_mileage(self):
        return self.annotate(mileage=Length("path", spheroid=True))


class Trip(models.Model):
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.RESTRICT,
        verbose_name="Предприятие",
        related_name="trips",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.RESTRICT,
        related_name="trips",
        verbose_name="Автомобиль",
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()

    objects = TripQuerySet.as_manager()
