import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create superuser from environment variables if it does not exist"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_NAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username:
            raise CommandError("DJANGO_SUPERUSER_NAME is required")

        if not password:
            raise CommandError("DJANGO_SUPERUSER_PASSWORD is required")

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists")
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{username}' created")
        )