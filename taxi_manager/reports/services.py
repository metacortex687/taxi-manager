import uuid
from . import models
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle

from django.shortcuts import get_object_or_404


class ReportService:
    def create_report(self, report_type, params) -> uuid.UUID:
        model_report = self.get_model_report_by_type(report_type)

        create_params = params.copy()

        if "enterprise" in create_params:
            create_params["enterprise"] = get_object_or_404(
                Enterprise, pk=int(create_params["enterprise"])
            )

        if "vehicle" in create_params:
            create_params["vehicle"] = get_object_or_404(
                Vehicle, pk=int(create_params["vehicle"])
            )

        report = model_report.objects.create(**create_params)

        report.create_values()

        return report.uuid

    def get_model_report_by_type(self, report_type):
        return next(
            (x for x in models.Report.get_report_types() if x["name"] == report_type)
        )["report_class"]

    def get_report_by_uuid(self, report_type, report_uuid):
        return get_object_or_404(
            self.get_model_report_by_type(report_type), uuid=report_uuid
        )

    def get_available_reports(self):
        return [
            {
                "name": report_type["name"],
                "verbose_name": report_type["verbose_name"],
                "params": report_type["params"],
            }
            for report_type in models.Report.get_report_types()
        ]

    def get_params_value(self, report_type, user):
        return {
            "enterprise": None,
            "vehicle": None,
            "report_from": None,
            "report_to": None,
            "frequency": None
        }

    def get_result_headers(self, report_type):
        model_report = self.get_model_report_by_type(report_type)
        return model_report.get_result_model().get_table_headers()

    def get_result(self, report_type, uuid):
        report = self.get_report_by_uuid(report_type, uuid)
        results = report.get_results()
        
        return [
            {
                **result,
                "date": result["date"].isoformat(),

            }
            for result in results.values()  
        ]

