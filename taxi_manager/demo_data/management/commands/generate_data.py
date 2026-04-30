from django.core.management.base import BaseCommand, CommandError

from taxi_manager.demo_data.services import DemoDataGenerator


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
            help="Количество водителей в создаваемых предприятиях",
        )
        parser.add_argument(
            "-vh",
            "--vehicle",
            type=int,
            help="Количество автомобилей в создаваемых предприятиях",
        )
        parser.add_argument(
            "--seed",
            type=int,
            help="Параметр инициализации генератора псевдослучайных чисел",
        )

    def handle(self, *args, **options):
        self._check_options(options)

        enterprise_names = options["enterprise"]

        if isinstance(enterprise_names, str):
            enterprise_names = [enterprise_names]

        generator = DemoDataGenerator(stdout=self.stdout)

        generator.generate(
            enterprise_names=enterprise_names,
            count_drivers=options["driver"],
            count_vehicles=options["vehicle"],
            seed=options["seed"],
        )

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