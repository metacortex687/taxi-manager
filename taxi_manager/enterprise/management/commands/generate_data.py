from django.core.management.base import BaseCommand, CommandError

from ...models import Enterprise
from taxi_manager.vehicle.models import Driver

from faker import Faker

class Command(BaseCommand):
    help = "Добавление в базу сгенерированных данных"

    def add_arguments(self, parser):
        parser.add_argument("-e", "--enterprise", nargs="+", type=str, help="Перечислите имена создаваемых предприятий")
        parser.add_argument("-d", "--driver",  type=int, help="Колличество водителей в создаваемых предприятиях")


    def handle(self, *args, **options):   

        if not options["enterprise"]:
            raise CommandError("Параметр -e или --enterprise со списком создаваемых организаций обязателен.")     

        if not options["driver"]:
            raise CommandError("Параметр -d или --driver с количеством создаваемых водителей обязателен.")     

        if type(options["enterprise"]) is str:
            enterprise_name_list = [options["enterprise"]]        

        if type(options["enterprise"]) is list:
            enterprise_name_list = options["enterprise"]

        enterprises = []
        for name in enterprise_name_list:
            enterprises.append(Enterprise.objects.create(name = name, city = "City"))

        fake = Faker(["en_US","ru_RU"])
        Faker.seed(0)

        for i in range(options["driver"]):
            name = fake.unique.name().split(' ')
            Driver.objects.create(first_name = name[0] , last_name = name[1], enterprise = enterprises[i % len(enterprises)], TIN = fake.bothify(text="############"))
        
        # drivers = []
        # for i in range(options["driver"]):
        #     driver = Driver.objects.create()



        

        

