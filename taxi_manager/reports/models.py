from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle

from django.contrib.auth import get_user_model
from django.db import models

import uuid


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

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def get_result_model(self):
        raise NotImplementedError

    def get_results(self) -> models.QuerySet:
        return self.get_result_model().objects.filter(report=self).order_by("date")


class ReportValue(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    date = models.DateTimeField()

    class Meta:
        abstract = True


class FloatReportValue(ReportValue):
    value = models.FloatField()


class CarMileageReport(Report):
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    def get_result_model(self):
        return FloatReportValue


class DefaultUserValues(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    period_from = models.DateTimeField()
    period_to = models.DateTimeField()
    enterprise = models.ForeignKey(Enterprise, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
