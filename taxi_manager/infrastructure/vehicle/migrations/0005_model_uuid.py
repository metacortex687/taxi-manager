import uuid

from django.db import migrations, models


def populate_model_uuid(apps, schema_editor):
    Model = apps.get_model("vehicle", "Model")

    for model in Model.objects.filter(uuid__isnull=True).iterator():
        model.uuid = uuid.uuid4()
        model.save(update_fields=["uuid"])


class Migration(migrations.Migration):
    dependencies = [
        ("vehicle", "0004_vehicle_purchased_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="model",
            name="uuid",
            field=models.UUIDField(
                null=True,
                editable=False,
                verbose_name="UUID",
            ),
        ),
        migrations.RunPython(
            populate_model_uuid,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="model",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4,
                unique=True,
                editable=False,
                verbose_name="UUID",
            ),
        ),
    ]