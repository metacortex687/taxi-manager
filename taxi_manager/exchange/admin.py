from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .models import ExchangeItem

from django.db import models
from django.contrib.contenttypes.models import ContentType

from import_export import resources, fields


class SelectableDBAAliasResourceMixin:  # Нужен для тестов, что бы выбирать базу данных
    def __init__(self, db_alias: str, **kwargs):
        super().__init__(**kwargs)
        self.db_alias = db_alias

    def get_queryset(self):
        return self._meta.model.objects.using(self.db_alias).all()

    def do_instance_save(self, instance, is_create):
        instance.save(using=self.db_alias)


class TimeZoneResource(SelectableDBAAliasResourceMixin, resources.ModelResource):
    class Meta:
        model = TimeZone
        exclude = ("id",)
        import_id_fields = ("code",)


class EnterpriseResource(SelectableDBAAliasResourceMixin, resources.ModelResource):
    exchange_uuid = fields.Field(attribute="exchange_uuid", column_name="exchange_uuid")
    time_zone = fields.Field(attribute="time_zone__code", column_name="time_zone")

    class Meta:
        model = Enterprise
        exclude = ("id",)

    def export(self, **kwargs):
        self._ensure_exchange_uuids_exist()

        return super().export(**kwargs)

    def get_queryset(self):
        uuid_subquery = ExchangeItem.objects.db_manager(self.db_alias).filter(
            content_type=self._get_content_type(), object_id=models.OuterRef("pk")
        ).values("uuid")[:1]

        return super().get_queryset().annotate(
            exchange_uuid=models.Subquery(uuid_subquery)
        ).all()

    def _get_content_type(self):
        return ContentType.objects.db_manager(self.db_alias).get_for_model(Enterprise)

    def _ensure_exchange_uuids_exist(self):
        ExchangeItem.objects.using(self.db_alias).bulk_create(
            [
                ExchangeItem(content_type=self._get_content_type(), object_id=enterprise.pk)
                for enterprise in self.get_queryset().filter(exchange_uuid__isnull=True)
            ]
        )
