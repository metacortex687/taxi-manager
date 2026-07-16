
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("vehicle", "0005_model_uuid"),
    ]

    operations = [
        # Добавляем новую nullable-связь по Model.uuid.
        migrations.AddField(
            model_name="vehicle",
            name="model_new",
            field=models.ForeignKey(
                to="vehicle.model",
                to_field="uuid",
                db_column="model_uuid",
                null=True,
                related_name="+",
                on_delete=django.db.models.deletion.RESTRICT,
                verbose_name="Модель",
            ),
        ),

        # Переносим существующие ссылки:
        # model_id -> Model.id -> Model.uuid.
        migrations.RunSQL(
            sql="""
                UPDATE vehicle_vehicle AS vehicle
                SET model_uuid = model.uuid
                FROM vehicle_model AS model
                WHERE vehicle.model_id = model.id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Удаляем старую связь по bigint.
        migrations.RemoveField(
            model_name="vehicle",
            name="model",
        ),

        # Новая связь снова называется model.
        migrations.RenameField(
            model_name="vehicle",
            old_name="model_new",
            new_name="model",
        ),

        # Запрещаем NULL и приводим поле к итоговому состоянию модели.
        migrations.AlterField(
            model_name="vehicle",
            name="model",
            field=models.ForeignKey(
                to="vehicle.model",
                to_field="uuid",
                db_column="model_uuid",
                on_delete=django.db.models.deletion.RESTRICT,
                verbose_name="Модель",
            ),
        ),
    ]
