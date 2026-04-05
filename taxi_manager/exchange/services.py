from .resources import (
    TimeZoneResource,
    EnterpriseResource,
    ModelResource,
    VehicleResource,
    VehicleLocationResource,
    TripResource,
)

from django.db import transaction

import tablib
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO


class EnterprisePeriodExchangeService:
    def get_exchange_plan(self, enterprise, period_from, period_to):
        return [
            (
                "time_zones",
                TimeZoneResource,
                lambda queryset: queryset
            ),
            (
                "model",
                ModelResource,
                lambda queryset: queryset
            ),
            (
                "enterprises",
                EnterpriseResource,
                lambda queryset: queryset.filter(id=enterprise.id)
            ),   
            (
                "vehicles",
                VehicleResource,
                lambda queryset: queryset.filter(enterprise=enterprise)
            ),    
            (
                "vehicle_locations",
                VehicleLocationResource,
                lambda queryset: queryset.filter_enterprise(enterprise).filter_period(period_from, period_to)
            ),  
            (
                "trips",
                TripResource,
                lambda queryset: queryset.filter_enterprise(enterprise).filter_period(period_from, period_to)
            ),                               
        ]


    def export_archive(self, enterprise, period_from, period_to) -> BytesIO:
        buffer = BytesIO()
        with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as zip_file:
            for base_name, class_resource, filter in self.get_exchange_plan(enterprise, period_from, period_to):
                self._write_dataset(
                    base_name,
                    class_resource().export(queryset=filter(class_resource().get_queryset())),
                    zip_file,
                )

        buffer.seek(0)
        return buffer

    @transaction.atomic
    def import_archive(self, archive: BytesIO, **kwargs):
        archive.seek(0)

        with ZipFile(archive) as z_file:
            for base_name, class_resource, _ in self.get_exchange_plan(None, None, None):
                class_resource().import_data(self._read_dataset(base_name, z_file), **kwargs)


    def _read_dataset(self, basename, zip_file) -> tablib.Dataset:
        return tablib.Dataset().load(zip_file.read(basename + ".json"), format="json")

    def _write_dataset(self, basename, dataset: tablib.Dataset, zip_file):
        zip_file.writestr(basename + ".json", dataset.json)
