from taxi_manager.enterprise.models import Enterprise

from .resources import (
    TimeZoneResource,
    EnterpriseResource,
    ModelResource,
    VehicleResource,
    VehicleLocationResource,
    TripResource,
)
from .models import ExchangeItem

from django.db import transaction

import tablib
from zipfile import ZipFile, ZIP_DEFLATED
import json
from datetime import datetime
from io import BytesIO


class EnterprisePeriodExchangeService:
    def get_exchange_plan(self, enterprise, period_from, period_to):
        return [
            (
                "time_zones",
                TimeZoneResource,
                lambda queryset: queryset,
                False,
            ),
            (
                "model",
                ModelResource,
                lambda queryset: queryset,
                False,
            ),
            (
                "enterprises",
                EnterpriseResource,
                lambda queryset: queryset.filter(id=enterprise.id),
                False,
            ),   
            (
                "vehicles",
                VehicleResource,
                lambda queryset: queryset.filter(enterprise=enterprise),
                False,
            ),    
            (
                "vehicle_locations",
                VehicleLocationResource,
                lambda queryset: queryset.filter_enterprise(enterprise).filter_period(period_from, period_to),
                True,
            ),  
            (
                "trips",
                TripResource,
                lambda queryset: queryset.filter_enterprise(enterprise).filter_period(period_from, period_to),
                True,
            ),                               
        ]


    def export_archive(self, enterprise, period_from, period_to) -> BytesIO:
        buffer = BytesIO()
        with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as zip_file:
            
            for base_name, class_resource, filter, _ in self.get_exchange_plan(enterprise, period_from, period_to):
                self._write_dataset(
                    base_name,
                    class_resource().export(queryset=filter(class_resource().get_queryset())),
                    zip_file,
                )

            self._write_meta(zip_file, enterprise, period_from, period_to)

        buffer.seek(0)
        return buffer
    
    @transaction.atomic
    def import_archive(self, archive: BytesIO, **kwargs):
        archive.seek(0)

        with ZipFile(archive) as z_file:
            for base_name, class_resource, _, is_periodical in self.get_exchange_plan(None, None, None):
                if is_periodical:
                    continue
                class_resource().import_data(self._read_dataset(base_name, z_file), **kwargs)

            meta = self._read_meta(z_file)
 
            for base_name, class_resource, filter, is_periodical in self.get_exchange_plan(meta["enterprise"], meta["period_from"], meta["period_to"]):
                if not is_periodical:
                    continue

                filter(class_resource().get_queryset()).delete()

                class_resource().import_data(self._read_dataset(base_name, z_file), **kwargs)        


    def _read_dataset(self, basename, zip_file) -> tablib.Dataset:
        return tablib.Dataset().load(zip_file.read(basename + ".json"), format="json")

    def _write_dataset(self, basename, dataset: tablib.Dataset, zip_file):
        zip_file.writestr(basename + ".json", dataset.json)

    def _read_meta(self, z_file) -> json:
        meta = json.loads(z_file.read("meta.json"))

        meta["enterprise"] = ExchangeItem.get_instance(meta["enterprise"], Enterprise)
        meta["period_from"] = datetime.fromisoformat(meta["period_from"])
        meta["period_to"] = datetime.fromisoformat(meta["period_to"])   

        return meta     


    def _write_meta(self, zip_file, enterprise, period_from, period_to):
        meta = {
            "enterprise": str(ExchangeItem.get_uuid(enterprise, Enterprise)),
            "period_from": period_from.isoformat(),
            "period_to": period_to.isoformat(),
        }

        zip_file.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=4))


    def get_filename(self, enterprise, period_from, period_to):
        enterprise_name = enterprise.name.replace(" ", "_")

        return (
            f"{enterprise_name}_"
            f"{period_from:%Y-%m-%d_%H-%M-%S}_"
            f"{period_to:%Y-%m-%d_%H-%M-%S}.zip"
        )