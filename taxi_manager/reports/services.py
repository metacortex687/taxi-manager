import uuid
from . import models
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle
from taxi_manager.time_zones.models import TimeZone

from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime

from io import BytesIO

class ReportService:
    def verbouse_name(self, report_type):
        return next(
            (x for x in models.Report.get_report_types() if x["name"] == report_type)
        )["verbose_name"]
    
    def create_report(self, report_type, params, user) -> uuid.UUID:
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

        if "time_zone" in create_params and create_params["time_zone"]:
            create_params["time_zone"] = get_object_or_404(
               TimeZone,
                code=create_params["time_zone"],
            )

        if "period_from" in create_params:
           create_params["period_from"] = parse_datetime(create_params["period_from"])
        if "period_to" in create_params:
           create_params["period_to"] = parse_datetime(create_params["period_to"])

        report = model_report.objects.create(**create_params)

        self.save_default_values(user, params)

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

    def get_pdf_by_uuid(self, report_type, uuid) -> BytesIO:
        report = self.get_report_by_uuid(report_type, uuid)
        return BytesIO(report.get_pdf())

    def save_default_values(self, user, params):
        default_values, _ = models.DefaultUserValues.objects.get_or_create(user=user)

        if "frequency" in params:
            default_values.frequency = params["frequency"]

        if "period_from" in params:
            default_values.period_from = params["period_from"]

        if "period_to" in params:
            default_values.period_to = params["period_to"]

        if "enterprise" in params and params["enterprise"]:
            default_values.enterprise = get_object_or_404(
                Enterprise,
                pk=int(params["enterprise"]),
            )

        if "vehicle" in params and params["vehicle"]:
            default_values.vehicle = get_object_or_404(
                Vehicle,
                pk=int(params["vehicle"]),
            )

        default_values.save()

    def get_params_value(self, report_type, user):
        params_names = self.get_model_report_by_type(report_type).get_params()

        result = {param_name: None for param_name in params_names}

        default_values = models.DefaultUserValues.objects.filter(user=user).first()
        if default_values is None:
            return result

        if "frequency" in params_names:
            result["frequency"] = default_values.frequency

        if "period_from" in params_names:
            result["period_from"] = default_values.period_from

        if "period_to" in params_names:
            result["period_to"] = default_values.period_to

        if "enterprise" in params_names and default_values.enterprise is not None:
            result["enterprise"] = default_values.enterprise.id
            result["time_zone"] = default_values.enterprise.time_zone.code

        if "vehicle" in params_names and default_values.vehicle is not None:
            result["vehicle"] = default_values.vehicle.id

        return result

    def get_list_frequencies(self):
        return [
            {"id": code, "display_name": display_name}
            for (code, display_name) in models.REPORT_FREQUENCIES
        ]
