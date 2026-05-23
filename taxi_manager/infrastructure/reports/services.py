from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta

from taxi_manager.infrastructure.enterprise.reposipories import (
    EnterpriseRepository,
    VehicleRepository,
)
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
        self,
        trip_repository: TripReposipory,
        vehicle_repository: VehicleRepository,
        enterprise_repository: EnterpriseRepository,
    ):
        self.report_args_parser = self._create_report_parser()
        self.trip_repository = trip_repository
        self.vehicle_repository = vehicle_repository
        self.enterprise_repository = enterprise_repository

    def list_reports(self):
        return [
            "1. Пробег автомобиля за период:\n"
            "car_mileage --period <day|month> --number [гос.номер автомобиля] --date <ДД.ММ.ГГГГ> --min_mileage_km [км. минимальный пробег]\n"
            "Если не указать number результат будет по всем автомобилям менеджера\n"
            "Примеры:\n"
            "/report car_mileage --period day --number w132Vq --date 23.03.2026\n"
            "/report car_mileage --period month --number w132Vq --date 01.03.2026\n"
            "/report car_mileage --period year --number w132Vq --date 01.01.2026\n"
        ]

    def report(self, command_line: str, user_id: int) -> list[str]:
        print(command_line)

        args = self.report_args_parser.parse_args(command_line.split())

        if args.number:
            return self._report_one_car_vehicle(
                args.number, user_id, args.date, args.period
            )

        return self._report_manager_cars_vehicle(
            user_id, args.date, args.period, args.min_mileage_km
        )

    def _report_one_car_vehicle(
        self, car_number: str, user_id: str, date: str, period: str
    ):
        car_id = self.vehicle_repository.id_by_number(car_number)

        if not car_id:
            return [f"Автомобиля с номером {car_number} нет в базе."]

        if not self.vehicle_repository.user_have_access(car_id, user_id):
            return [f"У менеджера нет доступа к автомобилю {car_number}"]

        from_date, to_date = self._period_dates(
            date, period, self.vehicle_repository.time_zone(car_id)
        )

        result = self.trip_repository.mileage_km([car_id], from_date, to_date)

        if not result:
            return [f"По автомобилю {car_number} нет пробега за выбранный период"]

        text_result = "Автомобили:\n"
        for row in result:
            text_result += f"{row['number']} пробег {row['mileage']:.0f} км."

        return [text_result]

    def _report_manager_cars_vehicle(
        self, user_id: str, date: str, period: str, min_mileage_km: float | None
    ):
        enterprise_ids = self.enterprise_repository.manager_enterprise_ids(user_id)

        if not enterprise_ids:
            return ["У менеджера нет назначенных предприятий"]

        result = []
        for enterprise_id in enterprise_ids:
            result.extend(
                self._report_enterprise_cars_vehicle(
                    enterprise_id, date, period, min_mileage_km
                )
            )

        if not result:
            result = ["По предприятиям менеджера нет маршрутов удовлетворяющих условию"]


        return result

    def _report_enterprise_cars_vehicle(
        self, enterprise_id: str, date: str, period: str, min_mileage_km: float | None
    ):
        enterprises_info = self.enterprise_repository.enterprises_info_dict(
            [enterprise_id]
        )

        time_zone = self.enterprise_repository.time_zone(enterprise_id)
        from_date, to_date = self._period_dates(date, period, time_zone)

        vehicles = self.enterprise_repository.vehicle_ids(enterprise_id)

        result = self.trip_repository.mileage_km(
            vehicles, from_date, to_date, min_mileage_km
        )

        if not result:
            return []

        text_result = f"Автомобили {enterprises_info[enterprise_id]['name']}:\n"
        for row in result:
            text_result += f"{row['number']} пробег {row['mileage']:.0f} км. \n"

        return [text_result]

    def _period_dates(self, date: str, period: str, tzinfo: ZoneInfo):
        date = datetime.strptime(date, "%d.%m.%Y").replace(tzinfo=tzinfo)

        if period == "day":
            return date, date + timedelta(day=1)

        if period == "month":
            return date, date + relativedelta(months=1)

        if period == "year":
            return date, date + relativedelta(years=1)

        raise NotImplementedError

    def _create_report_parser(self):
        report_parser = argparse.ArgumentParser()
        report_parser.add_argument("report_name")
        report_parser.add_argument("--period", required=True)
        report_parser.add_argument("--date", type=str, required=True)
        report_parser.add_argument("--number", type=str)
        report_parser.add_argument("--min_mileage_km", type=float)

        return report_parser
