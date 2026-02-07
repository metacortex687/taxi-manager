from django.core.management.base import BaseCommand, CommandError

from ...models import Enterprise
from taxi_manager.vehicle.models import Driver, Model, Vehicle

from faker import Faker
import random

class Command(BaseCommand):
    help = "Добавление в базу сгенерированных данных"

    def add_arguments(self, parser):
        parser.add_argument("-e", "--enterprise", nargs="+", type=str, help="Перечислите имена создаваемых предприятий")
        parser.add_argument("-d", "--driver",  type=int, help="Колличество водителей в создаваемых предприятиях")
        parser.add_argument("-vh", "--vehicle",  type=int, help="Колличество автомобилей в создаваемых предприятиях")


    def handle(self, *args, **options):   

        if not options["enterprise"]:
            raise CommandError("Параметр -e или --enterprise со списком создаваемых организаций обязателен.")     

        if not options["driver"]:
            raise CommandError("Параметр -d или --driver с количеством создаваемых водителей обязателен.")     
        
        if not options["vehicle"]:
            raise CommandError("Параметр -vh или --vehicle с количеством создаваемых автомобилей обязателен.")     

        if type(options["enterprise"]) is str:
            enterprise_name_list = [options["enterprise"]]        

        if type(options["enterprise"]) is list:
            enterprise_name_list = options["enterprise"]

        enterprises = []
        for name in enterprise_name_list:
            enterprise = Enterprise.objects.create(name = name, city = "City")
            enterprises.append(enterprise)

        fake = Faker(["en_US","ru_RU"])
        seed = 0
        Faker.seed(seed)
        random.seed(seed)

        for i in range(options["driver"]):
            name = fake.unique.name().split(' ')
            Driver.objects.create(first_name = name[0] , last_name = name[1], enterprise = enterprises[i % len(enterprises)], TIN = fake.bothify(text="############"))
        

        models = []
        models.append(Model.objects.create(name = "Нива внедорожник", type = "PCR", number_of_seats = 5, tank_capacity_l = 42, load_capacity_kg = 400))
        models.append(Model.objects.create(name = "Камаз", type = "LRR", number_of_seats = 2, tank_capacity_l = 500, load_capacity_kg = 5700))
        models.append(Model.objects.create(name = "Икарус", type = "BUS", number_of_seats = 34, tank_capacity_l = 250, load_capacity_kg = 5000))
        models.append(Model.objects.create(name = "BMW", type = "PCR", number_of_seats = 5, tank_capacity_l = 40, load_capacity_kg = 420))
        models.append(Model.objects.create(name = "Ford", type = "PCR", number_of_seats = 5, tank_capacity_l = 45, load_capacity_kg = 400))


        for i in range(options["vehicle"]):
            Vehicle.objects.create(price = random.randint(500,6000000), year_of_manufacture = random.randint(1980,2026), 
                               mileage = random.randint(1,300000), number = fake.bothify(text="?###??"),
                               vin = fake.vin(), model = models[0], enterprise = enterprises[0])

        # drivers = []
        # for i in range(options["driver"]):
        #     driver = Driver.objects.create()



        

        

