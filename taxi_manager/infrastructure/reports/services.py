from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from taxi_manager.infrastructure.enterprise.reposipories import VehicleRepository
from taxi_manager.infrastructure.geocoding.reposipories import TripReposipory
from taxi_manager.raw_application.chat_bot.interfaces import IChatReportService

from . import models
from . import tasks

from taxi_manager.infrastructure.enterprise.models import Enterprise
from taxi_manager.infrastructure.vehicle.models import Vehicle
from taxi_manager.infrastructure.time_zones.models import TimeZone

from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.db import transaction

import argparse
from io import BytesIO
import uuid


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

        self.save_default_values(user, params)

        report = model_report.objects.create(status="PENDING", **create_params)

        transaction.on_commit(
            lambda: tasks.build_report.enqueue(report_type, str(report.uuid))
        )

        return report.uuid

    def get_model_report_by_type(self, report_type):
        return next(
            (x for x in models.Report.get_report_types() if x["name"] == report_type)
        )["report_class"]

    def get_report_by_uuid(self, report_type, report_uuid):
        return get_object_or_404(
            self.get_model_report_by_type(report_type), uuid=report_uuid
        )

    def get_status(self, report_type, uuid):
        return self.get_report_by_uuid(report_type, uuid).status

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

        if report.status != "DONE":
            return []

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
        pdf_render = self.get_model_report_by_type(report_type).get_pdf_render()
        return BytesIO(pdf_render(report))

    def can_render_pdf(self, report_type) -> bool:
        return self.get_model_report_by_type(report_type).get_pdf_render() is not None

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

    def get_file_name_pdf_by_uuid(self, report_type, uuid):
        report = self.get_report_by_uuid(report_type, uuid)
        return f"{report.name}.pdf"


class ChatReportService(IChatReportService):
    def __init__(
        self, trip_repository: TripReposipory, vehicle_repository: VehicleRepository
    ):
        self.report_args_parser = self._create_report_parser()
        self.trip_repository = trip_repository
        self.vehicle_repository = vehicle_repository

    def list_reports(self):
        return [
                "1. Пробег автомобиля за период:\n"
                "car_mileage --period <day|month> --car_id <id_автомобиля> --date <ДД.ММ.ГГГГ>\n"
                "Примеры:\n"
                "/report car_mileage --period day --car_id 117 --date 23.03.2026\n"
                "/report car_mileage --period month --car_id 117 --date 01.03.2026"
        ]

    def report(self, command_line: str, user_id: int) -> list[str]:
        print(command_line)

        args = self.report_args_parser.parse_args(command_line.split())

        if not self.vehicle_repository.user_have_access(args.car_id, user_id):
            return [f"Нет доступа к автомобилю id={args.car_id}"]

        period = args.period
        date = datetime.strptime(args.date, "%d.%m.%Y").replace(
            tzinfo=self.vehicle_repository.time_zone(args.car_id)
        )

        if period == "day":
            return self.car_mileage_day(args.car_id, date)

        if period == "month":
            return self.car_mileage_month(args.car_id, date)

        return [str(args)]

    def _create_report_parser(self):
        report_parser = argparse.ArgumentParser()
        report_parser.add_argument("report_name")
        report_parser.add_argument("--period", required=True)
        report_parser.add_argument("--date", type=str, required=True)
        report_parser.add_argument("--car_id", type=int, required=True)
        return report_parser

    def car_mileage_day(self, car_id, date_day):
        result_report = self.trip_repository.mileage_km(
            car_id, date_day, date_day + timedelta(day=1)
        )

        if not result_report:
            return [f"По автомобилю id={car_id} нет пробега за выбранный период"]

        return [f"По автомобилю  id={car_id} пробег {result_report}км за выбранный период"]

    def car_mileage_month(self, car_id, date_month):
        result_report = self.trip_repository.mileage_km(
            car_id, date_month, date_month + relativedelta(months=1)
        )

        if not result_report:
            return [f"По автомобилю id={car_id} нет пробега за выбранный период"]

        return [f"По автомобилю  id={car_id} пробег {result_report} км за выбранный период"]    
