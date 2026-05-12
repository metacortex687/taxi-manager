# taxi_manager/demo_data/services.py

import random

from django.db import transaction
from django.db.models import Q
from faker import Faker
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.utils import timezone


from taxi_manager.infrastructure.enterprise.models import Enterprise
from taxi_manager.infrastructure.vehicle.models import (
    Driver,
    Model,
    Vehicle,
    VehicleDriver,
)
from taxi_manager.infrastructure.time_zones.models import TimeZone

from taxi_manager.infrastructure.demo_data.tracking_generator import TrackingGenerator
from taxi_manager.infrastructure.geo_tracking.models import Trip, VehicleLocation


class DemoDataGenerator:
    def __init__(self, stdout=None):
        self.stdout = stdout

    def write(self, message):
        if self.stdout:
            self.stdout.write(message)

    @transaction.atomic
    def generate(self, enterprise_names, count_drivers, count_vehicles, seed=None):
        fake = Faker(["en_US", "ru_RU"])

        Faker.seed(0)
        random.seed(0)

        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        models = self._generate_models()

        for enterprise_name in enterprise_names:
            self._generate_data_for_enterprise(
                enterprise_name=enterprise_name,
                count_vehicles=count_vehicles,
                count_drivers=count_drivers,
                fake=fake,
                models=models,
            )

    def _generate_data_for_enterprise(
        self, enterprise_name, count_drivers, count_vehicles, fake, models
    ):
        time_zone = TimeZone.objects.filter(code="UTC").first()

        if time_zone is None:
            time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)

        enterprise = Enterprise.objects.create(
            name=enterprise_name,
            city="City",
            time_zone=time_zone,
        )

        self.write(f"Создано предприятие {enterprise_name}")

        drivers = self._generate_drivers(count_drivers, enterprise, fake)
        vehicles = self._generate_vehicles(count_vehicles, enterprise, fake, models)

        random.shuffle(vehicles)
        random.shuffle(drivers)

        pairs = self._generate_vehicle_driver_pairs(drivers, vehicles, enterprise)

        random.shuffle(pairs)

        need_active_vehicle = 1 + len(vehicles) // 10

        self._set_active_pairs(pairs, need_active_vehicle)

    def _set_active_pairs(self, pairs, need_active_vehicle):
        active_pairs = []
        set_active_vehicle = set()
        set_active_driver = set()

        for vehicle, driver in pairs:
            if need_active_vehicle == 0:
                break

            if vehicle in set_active_vehicle:
                continue

            if driver in set_active_driver:
                continue

            active_pairs.append((vehicle, driver))

            set_active_vehicle.add(vehicle)
            set_active_driver.add(driver)

            need_active_vehicle -= 1

        q = Q()

        for vehicle, driver in active_pairs:
            q |= Q(vehicle=vehicle, driver=driver)

        if active_pairs:
            VehicleDriver.objects.filter(q).update(active=True)

        self.write(f"Назначено активных транспортных средств {len(active_pairs)}")

    def _generate_vehicle_driver_pairs(self, drivers, vehicles, enterprise):
        pairs = []

        start_idx_driver = 0

        for vehicle in vehicles:
            if len(drivers) == 0:
                continue

            count_assigned_drivers = min(len(drivers), random.randint(1, 5))
            end_idx_driver = min(
                len(drivers) - 1,
                start_idx_driver + count_assigned_drivers,
            )

            assigned_drivers = drivers[start_idx_driver : (end_idx_driver + 1)]

            vehicle.drivers.add(
                *assigned_drivers,
                through_defaults={"enterprise": enterprise},
            )

            for driver in assigned_drivers:
                pairs.append((vehicle, driver))

                assert vehicle.enterprise == enterprise
                assert driver.enterprise == enterprise

            start_idx_driver += count_assigned_drivers
            start_idx_driver %= len(drivers)

        self.write(f"Прикреплено водителей и машин {len(pairs)}")

        return pairs

    def _generate_vehicles(self, count_vehicles, enterprise, fake, models):
        vehicles = []

        for i in range(count_vehicles):
            vehicle = Vehicle.objects.create(
                price=random.randint(500, 6000000),
                year_of_manufacture=random.randint(1980, 2026),
                mileage=random.randint(1, 300000),
                number=fake.bothify(text="?###??"),
                vin=fake.vin(),
                model=models[i % len(models)],
                enterprise=enterprise,
            )

            vehicles.append(vehicle)

        self.write(f"Закуплено {len(vehicles)} транспортных средств")

        return vehicles

    def _generate_models(self):
        models = [
            Model.objects.create(
                name="Нива внедорожник",
                type="PCR",
                number_of_seats=5,
                tank_capacity_l=42,
                load_capacity_kg=400,
            ),
            Model.objects.create(
                name="Камаз",
                type="LRR",
                number_of_seats=2,
                tank_capacity_l=500,
                load_capacity_kg=5700,
            ),
            Model.objects.create(
                name="Икарус",
                type="BUS",
                number_of_seats=34,
                tank_capacity_l=250,
                load_capacity_kg=5000,
            ),
            Model.objects.create(
                name="BMW",
                type="PCR",
                number_of_seats=5,
                tank_capacity_l=40,
                load_capacity_kg=420,
            ),
            Model.objects.create(
                name="Ford",
                type="PCR",
                number_of_seats=5,
                tank_capacity_l=45,
                load_capacity_kg=400,
            ),
        ]

        self.write(f"Описано {len(models)} моделей")

        return models

    def _generate_drivers(self, count_drivers, enterprise, fake):
        drivers = []

        for i in range(count_drivers):
            name = fake.unique.name().split(" ")

            driver = Driver.objects.create(
                first_name=name[0],
                last_name=name[1],
                enterprise=enterprise,
                TIN=fake.bothify(text="############"),
            )

            drivers.append(driver)

        self.write(f"Нанято на работу {len(drivers)} водителей")

        return drivers

    @transaction.atomic
    def generate_trip(
        self,
        vehicle,
        location,
        distance_km,
        speed_km_h,
        delta_time_s,
        start_time=None,
        seed=0,
    ):
        self.write("Построение маршрута...")

        tracking_generator = TrackingGenerator(random.Random(seed))
        points = tracking_generator.generate_tracking_points_for_location(
            location,
            distance_km,
            speed_km_h,
            delta_time_s,
        )

        self.write(f"Маршрут построен, {len(points)} точек.")

        if not points:
            self.write("Точки не сгенерированы.")
            return None

        if start_time is None:
            start_time = timezone.now()

        enterprise = vehicle.enterprise

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

        trip = Trip.objects.create(
            enterprise=enterprise,
            vehicle=vehicle,
            started_at=start_time,
            ended_at=end_time,
        )

        self.write(f"Сгенерированы точки за период {start_time}-{end_time}")
        self.write(f"Создана поездка id={trip.id}")

        return trip
