import uuid
from . import models
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle

from django.shortcuts import get_object_or_404


class ReportService:
    def create_report(self, report_type, params) -> uuid.UUID:
        report = next(
            (x for x in models.Report.get_report_types() if x["name"] == report_type)
        )

        create_params = params.copy()
        
        if "enterprise" in create_params:
            create_params["enterprise" ] = get_object_or_404(Enterprise, pk=int(create_params["enterprise" ]))

        if "vehicle" in create_params:
            create_params["vehicle" ] = get_object_or_404(Vehicle, pk=int(create_params["vehicle" ]))

        report["report_class"].objects.create(**create_params)

        return uuid.uuid4()

    def get_available_reports(self):
        [
            {
                "name": report_type["name"],
                "verbose_name": report_type["verbose_name"],
                "params": report_type["params"],
            }
            for report_type in models.Report.get_report_types()
        ]
