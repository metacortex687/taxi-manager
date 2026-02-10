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

        fake = Faker(["en_US", "ru_RU"])
        Faker.seed(0)
        random.seed(0)
        if options["seed"]:
            Faker.seed(options["seed"])
            random.seed(options["seed"])

        models = self._generate_models()

        for enterprise_name in enterprise_name_list:
            self._generate_data_for_enterprise(enterprise_name = enterprise_name, count_vehicles = options["vehicle"], count_drivers =  options["driver"], fake=fake, models = models)    
   
        

    def _generate_data_for_enterprise(self, enterprise_name:str, count_drivers, count_vehicles, fake: Faker, models):
        enterprise = Enterprise.objects.create(name=enterprise_name, city="City")
        self.stdout.write(f"Создано предприятие {len(enterprise_name)} предприятий")
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

        VehicleDriver.objects.filter(q).update(active=True)

        self.stdout.write(f"Назначено активных транспортных средств {len(active_pairs)}")

    def _generate_vehicle_driver_pairs(self, drivers, vehicles, enterprise):

        pairs = []

        start_idx_driver = 0
        for vehicle in vehicles:
            if len(drivers) == 0:
                continue

            count_assigned_drivers = min(len(drivers), random.randint(1, 5))
            end_idx_driver = min(len(drivers)-1,start_idx_driver+count_assigned_drivers)
            vehicle.drivers.add(
                *drivers[start_idx_driver:(end_idx_driver+1)],
                through_defaults={"enterprise": enterprise},
            )

            for driver in drivers[start_idx_driver:(end_idx_driver+1)]:
                pairs.append((vehicle, driver))
                assert vehicle.enterprise == enterprise
                assert driver.enterprise == enterprise

            start_idx_driver += count_assigned_drivers
            start_idx_driver %= len(drivers)

        self.stdout.write(f"Прекреплено водителей и машин {len(pairs)}")

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
                model=models[i%len(models)],
                enterprise=enterprise,
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

        self.stdout.write(f"Нанято на работу {len(drivers)} водтелей")

        return drivers



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
