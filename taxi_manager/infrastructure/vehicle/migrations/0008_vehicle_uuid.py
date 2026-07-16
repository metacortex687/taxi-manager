import uuid

from django.db import migrations, models


def populate_vehicle_uuid(apps, schema_editor):
    Vehicle = apps.get_model("vehicle", "Vehicle")

    for vehicle in Vehicle.objects.filter(uuid__isnull=True).iterator():
        vehicle.uuid = uuid.uuid4()
        vehicle.save(update_fields=["uuid"])


class Migration(migrations.Migration):
    dependencies = [
        ("vehicle", "0007_alter_vehicle_enterprise"),
    ]

    operations = [
        migrations.AddField(
            model_name="vehicle",
            name="uuid",
            field=models.UUIDField(
                null=True,
                editable=False,
                verbose_name="UUID",
            ),
        ),
        migrations.RunPython(
            populate_vehicle_uuid,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="vehicle",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                verbose_name="UUID",
            ),
        ),
    ]