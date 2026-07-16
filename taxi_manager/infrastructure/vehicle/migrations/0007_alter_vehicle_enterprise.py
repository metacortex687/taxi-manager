import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vehicle", "0006_alter_vehicle_model"),
    ]

    operations = [
        # Временно добавляем новую nullable-связь по Enterprise.uuid.
        migrations.AddField(
            model_name="vehicle",
            name="enterprise_new",
            field=models.ForeignKey(
                to="enterprise.enterprise",
                to_field="uuid",
                db_column="enterprise_uuid",
                null=True,
                related_name="+",
                on_delete=django.db.models.deletion.RESTRICT,
                verbose_name="Предприятие",
            ),
        ),

        # Переносим существующие ссылки:
        # enterprise_id -> Enterprise.id -> Enterprise.uuid.
        migrations.RunSQL(
            sql="""
                UPDATE vehicle_vehicle AS vehicle
                SET enterprise_uuid = enterprise.uuid
                FROM enterprise_enterprise AS enterprise
                WHERE vehicle.enterprise_id = enterprise.id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Удаляем старую связь по bigint.
        migrations.RemoveField(
            model_name="vehicle",
            name="enterprise",
        ),

        # Новая связь снова называется enterprise.
        migrations.RenameField(
            model_name="vehicle",
            old_name="enterprise_new",
            new_name="enterprise",
        ),

        # Запрещаем NULL и приводим поле к состоянию модели.
        migrations.AlterField(
            model_name="vehicle",
            name="enterprise",
            field=models.ForeignKey(
                to="enterprise.enterprise",
                to_field="uuid",
                db_column="enterprise_uuid",
                related_name="vehicles",
                on_delete=django.db.models.deletion.RESTRICT,
                verbose_name="Предприятие",
            ),
        ),
    ]