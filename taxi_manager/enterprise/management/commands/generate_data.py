from django.core.management.base import BaseCommand, CommandError

from ...models import Enterprise

class Command(BaseCommand):
    help = "Добавление в базу сгенерированных данных"

    def add_arguments(self, parser):
        parser.add_argument("-e", "--enterprise", nargs="+", type=str, help="Перечислите имена создаваемых предприятий")


    def handle(self, *args, **options):   

        if not options["enterprise"]:
            raise CommandError("Параметр -e или --enterprise со списком создаваемых организаций обязателен.")      

        if type(options["enterprise"]) is str:
            enterprise_name_list = [options["enterprise"]]        

        if type(options["enterprise"]) is list:
            enterprise_name_list = options["enterprise"]

        for name in enterprise_name_list:
            Enterprise.objects.create(name = name, city = "City")

        

