from django.core.management.base import BaseCommand

from taxi_manager.demo_data.services import DemoDataGenerator
from taxi_manager.vehicle.models import Vehicle


class Command(BaseCommand):
    help = (
        "Добавление в базу сгенерированных данных трекинга по автомобилю.\n"
        "generate_tracking_data -v_id 117 -l 'Moscow' -ds 5 -s 40 -dt 10"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "-v_id",
            "--vehicle_id",
            type=int,
            required=True,
            help="Автомобиль по которому генерировать данные",
        )
        parser.add_argument(
            "-l",
            "--location",
            type=str,
            required=True,
            help="Населенный пункт: 'Moscow'",
        )
        parser.add_argument(
            "-ds",
            "--distance_km",
            type=float,
            required=True,
            help="Длина генерируемого пути (км)",
        )
        parser.add_argument(
            "-s",
            "--speed_km_h",
            type=float,
            required=True,
            help="Скорость транспортного средства (км/ч)",
        )
        parser.add_argument(
            "-dt",
            "--delta_time_s",
            type=float,
            required=True,
            help="Интервал между точками трекинга (сек)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Начало генерации данных...")

        vehicle = Vehicle.objects.get(id=options["vehicle_id"])

        generator = DemoDataGenerator(stdout=self.stdout)
        generator.generate_trip(
            vehicle=vehicle,
            location=options["location"],
            distance_km=options["distance_km"],
            speed_km_h=options["speed_km_h"],
            delta_time_s=options["delta_time_s"],
        )

        self.stdout.write("Генерация данных завершена.")