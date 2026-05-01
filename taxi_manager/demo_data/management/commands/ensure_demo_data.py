from datetime import datetime, timedelta
import random

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from taxi_manager.demo_data.services import DemoDataGenerator
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle


DEMO_ENTERPRISE_NAMES = [
    "ПредприятиеКирилица",
    "Enterprise 1",
    "Enterprise 2",
]

VEHICLES_PER_ENTERPRISE = 10
TOTAL_DRIVERS = 15
TRIPS_PER_VEHICLE = 10
DEMO_START_DATE = datetime(2023, 1, 1, 8, 0, 0)


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Заполнение базы демо данными при необходимости")

        if Enterprise.objects.filter(name__in=DEMO_ENTERPRISE_NAMES).exists():
            self.stdout.write("Демо данные уже существуют, заполнение не требуется")
            return

        if TOTAL_DRIVERS % len(DEMO_ENTERPRISE_NAMES) != 0:
            raise CommandError("TOTAL_DRIVERS должен делиться на количество предприятий")

        drivers_per_enterprise = TOTAL_DRIVERS // len(DEMO_ENTERPRISE_NAMES)

        generator = DemoDataGenerator(stdout=self.stdout)

        generator.generate(
            enterprise_names=DEMO_ENTERPRISE_NAMES,
            count_drivers=drivers_per_enterprise,
            count_vehicles=VEHICLES_PER_ENTERPRISE,
            seed=0,
        )

        self._generate_trips(generator)

        self.stdout.write(self.style.SUCCESS("Демо данные успешно созданы"))

    def _generate_trips(self, generator):
        vehicles = list(
            Vehicle.objects.filter(
                enterprise__name__in=DEMO_ENTERPRISE_NAMES,
            )
            .select_related("enterprise")
            .order_by("enterprise__name", "id")
        )

        if not vehicles:
            raise CommandError("Не найдены автомобили для генерации поездок")

        period_from = timezone.make_aware(DEMO_START_DATE)
        period_to = timezone.now()
        period_seconds = (period_to - period_from).total_seconds()

        total_trips = len(vehicles) * TRIPS_PER_VEHICLE
        rng = random.Random(0)

        created_trips = 0

        for vehicle_index, vehicle in enumerate(vehicles):
            for trip_index in range(TRIPS_PER_VEHICLE):
                global_trip_index = vehicle_index * TRIPS_PER_VEHICLE + trip_index
                ratio = global_trip_index / max(total_trips - 1, 1)

                start_time = period_from + timedelta(seconds=period_seconds * ratio)

                generator.generate_trip(
                    vehicle=vehicle,
                    location="Moscow",
                    distance_km=rng.uniform(2, 50),
                    speed_km_h=rng.uniform(30, 60),
                    delta_time_s=60,
                    start_time=start_time,
                    seed=global_trip_index,
                )

                created_trips += 1

        self.stdout.write(f"Создано поездок: {created_trips}")