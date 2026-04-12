from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle
from taxi_manager.geo_tracking.models import Trip
from taxi_manager.time_zones.models import TimeZone

from . import pdf

from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.db.models import Sum, Count
from django.contrib.auth import get_user_model
from django.db import models
from django.apps import apps

from zoneinfo import ZoneInfo

import uuid
import json



REPORT_FREQUENCIES = [
    ("DAY", "День"),
    ("WEEK", "Неделя"),
    ("MONTH", "Месяц"),
    ("YEAR", "Год"),
]


class Report(models.Model):
    name = models.CharField(max_length=500)
    frequency = models.CharField(max_length=5, choices=REPORT_FREQUENCIES)
    period_from = models.DateTimeField()
    period_to = models.DateTimeField()
    time_zone = models.ForeignKey(TimeZone, on_delete=models.RESTRICT)

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    @classmethod
    def get_result_model(cls):
        raise NotImplementedError
    
    def create_values(self):
        raise NotImplementedError


    def get_results(self) -> models.QuerySet:
        return self.get_result_model().objects.filter(report=self).order_by("date")

    def save(self, *args, **kwargs):
        report_tz = ZoneInfo(self.time_zone.code)
        self.period_from    = self.period_from.astimezone(report_tz)
        self.period_to      = self.period_to.astimezone(report_tz)
        super().save(*args, **kwargs)

    def get_pdf(self):
        return pdf.renderReportToPDF(self)

    @classmethod
    def get_report_types(cls):
        return [
            {
                "name": model._meta.model_name,
                "verbose_name": model._meta.verbose_name,
                "report_class": model,
                "params": model.get_params()
            }
            for model in filter(
                lambda model: issubclass(model, cls) and model is not cls,
                apps.get_models(),
            )
        ]

    @classmethod
    def get_params(cls):
        return ["frequency", "period_from", "period_to"]


    def trunc_date(self, field_name):
        return {
            "DAY": TruncDay,
            "WEEK": TruncWeek,
            "MONTH": TruncMonth,
            "YEAR": TruncYear,
        }[self.frequency](field_name, tzinfo=ZoneInfo(self.time_zone.code))

         



class ReportValue(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Дата")

    class Meta:
        abstract = True

    @classmethod
    def get_table_fields(cls):
        return [
            field.name
            for field in cls._meta.fields
            if field.name not in ["id", "report"]
        ]

    @classmethod
    def get_table_headers(cls):
        return [
            {
                "name": field_name,
                "verbose_name": cls._meta.get_field(field_name).verbose_name,
            }
            for field_name in cls.get_table_fields()
        ]

class CarMileageReportValue(ReportValue):
    mileage = models.FloatField(verbose_name="Пробег, км")
    count_trip = models.IntegerField(verbose_name="Поездок")


class CarMileageReport(Report):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Пробег автомобиля"

    @classmethod
    def get_params(cls):
        return super().get_params() + ["enterprise", "vehicle"]

    @classmethod
    def get_result_model(cls):
        return CarMileageReportValue
    
    def get_pdf(self):
        return pdf.renderReportToPDF(self)


    def create_values(self):
        grouped_rows = (
            Trip.objects.filter_enterprise(self.enterprise)
            .filter_vehicle(self.vehicle)
            .filter_period(self.period_from, self.period_to)
            .annotate_path()
            .annotate_mileage()
            .annotate(date=self.trunc_date("started_at"))
            .values("date")
            .annotate(mileage=Sum("mileage"))
            .annotate(count_trip=Count("id"))
        )

        values_to_create = [
            CarMileageReportValue(
                report=self,
                date=row["date"],
                mileage=row["mileage"].km,
                count_trip=row["count_trip"],
            )
            for row in grouped_rows
        ]

        CarMileageReportValue.objects.bulk_create(values_to_create)

class CarRoutesReportValue(ReportValue):
    path = models.JSONField(verbose_name="Маршруты")


class CarRoutesReport(Report):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Маршруты автомобилей"

    @classmethod
    def get_params(cls):
        return super().get_params() + ["enterprise"]

    @classmethod
    def get_result_model(cls):
        return CarRoutesReportValue

    def create_values(self):
        grouped_rows = (
            Trip.objects.filter_enterprise(self.enterprise)
            .filter_period(self.period_from, self.period_to)
            .annotate_path()
            .annotate(date=self.trunc_date("started_at"))
            .values("date", "path")
            .order_by("date")
        )

        paths_by_date = {}

        for row in grouped_rows:
            if row["date"] not in paths_by_date:
                paths_by_date[row["date"]] = []

            if row["path"] is not None:
                paths_by_date[row["date"]].append(json.loads(row["path"].geojson))

        CarRoutesReportValue.objects.bulk_create(
            [
                CarRoutesReportValue(
                    report=self,
                    date=date,
                    path=paths,
                )
                for date, paths in paths_by_date.items()
            ]
        )


class DefaultUserValues(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True)
    period_from = models.DateTimeField(null=True)
    period_to = models.DateTimeField(null=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE, null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True)
    frequency = models.CharField(max_length=5,choices=REPORT_FREQUENCIES, null=True)
