from django.core.management.base import BaseCommand, CommandError

from ...models import Enterprise
from taxi_manager.vehicle.models import Driver, Model, Vehicle, VehicleDriver

from faker import Faker
import random
from django.db.models import Subquery, Q
from django.db import transaction


class Command(BaseCommand):
    help = "Добавление в базу сгенерированных данных"

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--enterprise",
            nargs="+",
            type=str,
            help="Перечислите имена создаваемых предприятий",
        )
        parser.add_argument(
            "-d",
            "--driver",
            type=int,
            help="Колличество водителей в создаваемых предприятиях",
        )
        parser.add_argument(
            "-vh",
            "--vehicle",
            type=int,
            help="Колличество автомобилей в создаваемых предприятиях",
        )
        parser.add_argument(
            "--seed",
            type=int,
            help="Параметр инициализации генератора псевдослучайных чисел",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self._check_options(options)

        if type(options["enterprise"]) is str:
            enterprise_name_list = [options["enterprise"]]

        if type(options["enterprise"]) is list:
            enterprise_name_list = options["enterprise"]

        enterprises = self._genegate_enterprises(enterprise_name_list)

        fake = Faker(["en_US", "ru_RU"])
        Faker.seed(0)
        random.seed(0)
        if options["seed"]:
            Faker.seed(options["seed"])
            random.seed(options["seed"])

        drivers = self._generate_drivers(options, enterprises, fake)

        models = self._generate_models()

        vehicles = self._generate_vehicles(options, enterprises, fake, models)

        random.shuffle(vehicles)
        random.shuffle(drivers)

        pairs = self._generate_vehicle_driver_pairs(drivers, vehicles)

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

        VehicleDriver.objects.filter(q).update(active=True)

        self.stdout.write(f"Назначено активных транспортных средств {len(active_pairs)}")

    def _generate_vehicle_driver_pairs(self, drivers, vehicles):
        grouped_by_enterprise_data = dict()

        for vehicle in vehicles:
            if vehicle.enterprise not in grouped_by_enterprise_data:
                grouped_by_enterprise_data[vehicle.enterprise] = [], []
            _vehicles, _drivers = grouped_by_enterprise_data[vehicle.enterprise]

            if (
                random.randint(0, 10) != 0
            ):  # Каждое 10-е транспортное средство будет без прикрепленных водителей
                _vehicles.append(vehicle)

            grouped_by_enterprise_data[vehicle.enterprise] = _vehicles, _drivers

        for driver in drivers:
            if driver.enterprise not in grouped_by_enterprise_data:
                grouped_by_enterprise_data[driver.enterprise] = [], []

            _vehicles, _drivers = grouped_by_enterprise_data[vehicle.enterprise]

            if random.randint(0, 10) != 0:  # Каждый 10-й водитель без автомобилей
                _drivers.append(driver)

            grouped_by_enterprise_data[driver.enterprise] = _vehicles, _drivers

        pairs = []
        for enterprise, (_vehicles, _drivers) in grouped_by_enterprise_data.items():
            start_idx_driver = 0
            for vehicle in _vehicles:
                if len(_drivers) == 0:
                    continue

                count_assigned_drivers = min(len(_drivers), random.randint(1, 5))
                end_idx_driver = min(len(_drivers)-1,start_idx_driver+count_assigned_drivers)
                vehicle.drivers.add(
                    *_drivers[start_idx_driver:(end_idx_driver+1)],
                    through_defaults={"enterprise": enterprise},
                )

                for driver in _drivers[start_idx_driver:(end_idx_driver+1)]:
                    pairs.append((vehicle, driver))

                start_idx_driver += count_assigned_drivers
                start_idx_driver %= len(_drivers)

        self.stdout.write(f"Прекреплено водителей и машин {len(pairs)}")

        return pairs

    def _generate_vehicles(self, options, enterprises, fake, models):
        vehicles = []
        for i in range(options["vehicle"]):
            vehicle = Vehicle.objects.create(
                price=random.randint(500, 6000000),
                year_of_manufacture=random.randint(1980, 2026),
                mileage=random.randint(1, 300000),
                number=fake.bothify(text="?###??"),
                vin=fake.vin(),
                model=models[i%len(models)],
                enterprise=enterprises[i%len(enterprises)],
            )
            vehicles.append(vehicle)

        self.stdout.write(f"Закуплено {len(vehicles)} транспортных средств")

        return vehicles

    def _generate_models(self):
        models = []
        models.append(
            Model.objects.create(
                name="Нива внедорожник",
                type="PCR",
                number_of_seats=5,
                tank_capacity_l=42,
                load_capacity_kg=400,
            )
        )
        models.append(
            Model.objects.create(
                name="Камаз",
                type="LRR",
                number_of_seats=2,
                tank_capacity_l=500,
                load_capacity_kg=5700,
            )
        )
        models.append(
            Model.objects.create(
                name="Икарус",
                type="BUS",
                number_of_seats=34,
                tank_capacity_l=250,
                load_capacity_kg=5000,
            )
        )
        models.append(
            Model.objects.create(
                name="BMW",
                type="PCR",
                number_of_seats=5,
                tank_capacity_l=40,
                load_capacity_kg=420,
            )
        )
        models.append(
            Model.objects.create(
                name="Ford",
                type="PCR",
                number_of_seats=5,
                tank_capacity_l=45,
                load_capacity_kg=400,
            )
        )

        self.stdout.write(f"Описано {len(models)} моделей")

        return models

    def _generate_drivers(self, options, enterprises, fake):
        drivers = []
        for i in range(options["driver"]):
            name = fake.unique.name().split(" ")
            driver = Driver.objects.create(
                first_name=name[0],
                last_name=name[1],
                enterprise=enterprises[i % len(enterprises)],
                TIN=fake.bothify(text="############"),
            )
            drivers.append(driver)

        self.stdout.write(f"Нанято на работу {len(drivers)} водтелей")

        return drivers

    def _genegate_enterprises(self, enterprise_name_list):
        enterprises = []
        for name in enterprise_name_list:
            enterprise = Enterprise.objects.create(name=name, city="City")
            enterprises.append(enterprise)

        self.stdout.write(f"Создано {len(enterprises)} предприятий")

        return enterprises

    def _check_options(self, options):
        if not options["enterprise"]:
            raise CommandError(
                "Параметр -e или --enterprise со списком создаваемых организаций обязателен."
            )

        if not options["driver"]:
            raise CommandError(
                "Параметр -d или --driver с количеством создаваемых водителей обязателен."
            )

        if not options["vehicle"]:
            raise CommandError(
                "Параметр -vh или --vehicle с количеством создаваемых автомобилей обязателен."
            )
