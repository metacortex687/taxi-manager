from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vk_bot", "0002_create_pgwatch_trip_trigger"),
        ("django_pgwatch", "0002_install_pg_functions"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE SCHEMA IF NOT EXISTS services;

            ALTER TABLE IF EXISTS django_pgwatch_notificationlog
            SET SCHEMA services;
            """,
            reverse_sql="""
            ALTER TABLE IF EXISTS services.django_pgwatch_notificationlog
            SET SCHEMA public;
            """,
        ),
    ]