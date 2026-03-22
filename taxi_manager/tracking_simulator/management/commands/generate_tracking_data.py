from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.contrib.gis.geos import Point

from datetime import timedelta

from taxi_manager.tracking_simulator.tracking_generator import TrackingGenerator
from taxi_manager.geo_tracking.models import VehicleLocation
from taxi_manager.vehicle.models import Vehicle

class Command(BaseCommand):
    help = ("Добавление в базу сгенерированных данных трекинга по автомобилю.\n" 
    "generate_tracking_data -v_id 117 -l 'Moscow'  -ds 5 -s 40 -dt 10")

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
            help="Населенный пункт: 'Moscow",
        )
        parser.add_argument(
            "-ds",
            "--distance_km",
            type=float,
            required=True,
            help="Длинна генерируемого пути (км)",
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


    @transaction.atomic
    def handle(self, *args, **options):  
        self.stdout.write("Начало генерации данных...")
        location = options["location"]
        distance_km = options["distance_km"]
        speed_km_h = options["speed_km_h"]
        delta_time_s = options["delta_time_s"]


        self.stdout.write("Построение маршрута...")
        points = TrackingGenerator.generate_tracking_points_for_location(location, distance_km, speed_km_h, delta_time_s)
        self.stdout.write(f"Маршрут построен, {len(points)} точек.")
        
        self.stdout.write("Сохранение данных...")

        vehicle = Vehicle.objects.get(id=options["vehicle_id"])
        enterprise=vehicle.enterprise
        self.save_data(enterprise, vehicle, points)
        
        self.stdout.write("Генерация данных завершена.")


    def save_data(self, enterprise, vehicle, points):
        start_time = timezone.now()


        locations = []
        for lon, lat, seconds_from_start in points:
            locations.append(
                VehicleLocation(
                    enterprise=enterprise,
                    vehicle=vehicle,
                    location=Point(lon, lat, srid=4326),
                    tracked_at=start_time + timedelta(seconds=seconds_from_start),
                )
            )

        VehicleLocation.objects.bulk_create(locations)

        _, _, seconds_from_start = points[-1]
        end_time = start_time + timedelta(seconds=seconds_from_start)
        self.stdout.write(f"Сгенерированы точки за период {start_time}-{end_time}")

