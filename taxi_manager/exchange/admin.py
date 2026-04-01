from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .models import ExchangeItem

from django.db import models
from django.contrib.contenttypes.models import ContentType

from import_export import resources, fields, widgets

class TimeZoneResource(resources.ModelResource):
    class Meta:
        model = TimeZone
        exclude = ("id",)
        import_id_fields = ("code",)


class EnterpriseResource(resources.ModelResource):
    exchange_uuid = fields.Field(attribute="exchange_uuid", column_name="exchange_uuid")
    time_zone = fields.Field(attribute="time_zone", column_name="time_zone",  widget=widgets.ForeignKeyWidget(TimeZone, "code"),)

    class Meta:
        model = Enterprise
        fields = ("name", "city", "time_zone", "exchange_uuid")
        import_id_fields = ("exchange_uuid",)

    def get_queryset(self):
        uuid_subquery = (
            ExchangeItem.objects.filter(
                content_type=self._get_content_type(),
                object_id=models.OuterRef("pk"),
            )
            .values("uuid")[:1]
        )

        return super().get_queryset().annotate(
            exchange_uuid=models.Subquery(uuid_subquery)
        )

    def export(self, **kwargs):
        self._ensure_exchange_uuids_exist()

        return super().export(**kwargs)
    
    def get_instance(self, instance_loader, row):

        exchange_item = ExchangeItem.objects.filter(content_type=self._get_content_type(), uuid=row["exchange_uuid"]).first()
        
        if exchange_item is not None:
            return exchange_item.content_object

        return None
    
    def save_instance(self, instance, is_create, row, **kwargs):
        super().save_instance(instance, is_create, row, **kwargs)
    
        if not is_create:
            return
                
        ExchangeItem.objects.create(content_type=self._get_content_type(), uuid=row["exchange_uuid"], object_id=instance.id)


    def _ensure_exchange_uuids_exist(self):

        ExchangeItem.objects.bulk_create(
            [
                ExchangeItem(content_type=self._get_content_type(), object_id=enterprise.pk)
                for enterprise in self.get_queryset().filter(exchange_uuid__isnull=True)
            ]
        )

    def _get_content_type(self):
        return ContentType.objects.get_for_model(Enterprise)   