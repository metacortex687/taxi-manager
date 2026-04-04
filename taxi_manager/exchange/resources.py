from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone
from taxi_manager.vehicle.models import Model, Vehicle
from taxi_manager.geo_tracking.models import VehicleLocation

from .models import ExchangeItem

from django.db import models
from django.contrib.contenttypes.models import ContentType

from import_export import resources, fields, widgets, exceptions


class ExchangeUuidResource(resources.ModelResource):
    exchange_uuid = fields.Field(attribute="exchange_uuid", column_name="exchange_uuid")

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
        return ContentType.objects.get_for_model(self._meta.model)   


class TimeZoneResource(resources.ModelResource):
    class Meta:
        model = TimeZone
        fields = ("code","utc_offset",)
        import_id_fields = ("code",)

class ModelResource(resources.ModelResource):
    class Meta:
        model = Model
        fields = ("name","type","number_of_seats", "tank_capacity_l", "load_capacity_kg", "color")
        import_id_fields = ("name",)

class EnterpriseResource(ExchangeUuidResource):
    
    time_zone = fields.Field(attribute="time_zone", column_name="time_zone",  widget=widgets.ForeignKeyWidget(TimeZone, "code"),)

    class Meta:
        model = Enterprise
        fields = ("exchange_uuid", "name", "city", "time_zone")
        import_id_fields = ("exchange_uuid",)

class ForeignUuidKeyWidget(widgets.ForeignKeyWidget):
    def render(self, value, obj = None, **kwargs):
        if value is None:
            return ""

        exchange_item = ExchangeItem.objects.filter(content_type=self._get_content_type(), object_id=value.id).first()
        if exchange_item:
            return str(exchange_item.uuid)
        
        raise exceptions.FieldError(
            f"Невозможно выполнить экспорт значения: {value}: "
            f"связанный объект {self.model.__name__} не имеет exchange_uuid. "
            f"Сначала экспортируйте {self.model.__name__}, затем повторите экспорт."
        )            
    
    def clean(self, value, row = None, **kwargs):
        exchange_item = ExchangeItem.objects.filter(content_type=self._get_content_type(), uuid=value).first()
        if exchange_item:
            return super().clean(exchange_item.object_id, row, **kwargs)
        
        raise exceptions.FieldError(
            f"Невозможно выполнить импорт ссылки: {value}. "
            f"Сначала импортируйте объект {value} в {self.model.__name__}, затем повторите."
        )          

    def _get_content_type(self):
        return ExchangeItem.get_content_type_for_model(self.model)  



class VehicleResource(ExchangeUuidResource):

    model = fields.Field(attribute="model", column_name="model",  widget=widgets.ForeignKeyWidget(Model, "name")) 
    enterprise = fields.Field(attribute="enterprise", column_name="enterprise", widget=ForeignUuidKeyWidget(Enterprise, "id"))

    class Meta:
        model = Vehicle
        fields = ("exchange_uuid", "price", "year_of_manufacture", "mileage", "number", "vin", "model", "enterprise") #enterprise пока нет возможности внешний ключ по uuid
        import_id_fields = ("exchange_uuid",)


class VehicleLocationResource(resources.ModelResource):        
        enterprise = fields.Field(attribute="enterprise", column_name="enterprise", widget=ForeignUuidKeyWidget(Enterprise, "id"))
        vehicle = fields.Field(attribute="vehicle", column_name="vehicle", widget=ForeignUuidKeyWidget(Vehicle, "id"))
        tracked_at = fields.Field(attribute="tracked_at", column_name="tracked_at",widget=widgets.DateTimeWidget(format="%Y-%m-%d %H:%M:%S %z"))

        class Meta:
            model = VehicleLocation
            fields = ("enterprise", "vehicle", "location", "tracked_at")
            import_id_fields = ("enterprise","vehicle", "tracked_at")

        def export_data_for_enterprise_and_period(self, enterprise, period_from, period_to):
            return self.export(queryset=VehicleLocation.objects.all().filter_period(period_from, period_to).filter_enterprise(enterprise))


        def clear_and_import_data_for_enterprise_and_period(self, dataset, enterprise, period_from, period_to, **kwargs):
            VehicleLocation.objects.all().filter_period(period_from, period_to).filter_enterprise(enterprise).delete()

            self.import_data(dataset, **kwargs)









