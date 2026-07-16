
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("enterprise", "0005_alter_manager_enterprise"),
        ("users", "0002_user_uuid"),
    ]

    operations = [
        # Временно убираем UNIQUE(user_id, enterprise_uuid).
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="manager",
                    unique_together=set(),
                ),
            ],
        ),
        # Добавляем новую nullable-связь по User.uuid.
        migrations.AddField(
            model_name="manager",
            name="user_new",
            field=models.ForeignKey(
                to="users.user",
                to_field="uuid",
                db_column="user_uuid",
                null=True,
                related_name="+",
                on_delete=django.db.models.deletion.RESTRICT,
                verbose_name="Пользователь",
            ),
        ),

        # Переносим существующие ссылки:
        # user_id -> auth_user.id -> auth_user.uuid.
        migrations.RunSQL(
            sql="""
                UPDATE enterprise_manager AS manager
                SET user_uuid = auth_user.uuid
                FROM auth_user
                WHERE manager.user_id = auth_user.id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Удаляем старую связь по bigint.
        migrations.RemoveField(
            model_name="manager",
            name="user",
        ),

        # Новая связь снова называется user.
        migrations.RenameField(
            model_name="manager",
            old_name="user_new",
            new_name="user",
        ),

        # Запрещаем NULL и приводим поле к итоговому состоянию модели.
        migrations.AlterField(
            model_name="manager",
            name="user",
            field=models.ForeignKey(
                to="users.user",
                to_field="uuid",
                db_column="user_uuid",
                on_delete=django.db.models.deletion.RESTRICT,
                verbose_name="Пользователь",
            ),
        ),

        # Восстанавливаем UNIQUE(user_uuid, enterprise_uuid).
        migrations.AlterUniqueTogether(
            name="manager",
            unique_together={("user", "enterprise")},
        ),
    ]