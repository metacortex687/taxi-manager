from rest_framework import serializers
from taxi_manager.vehicle.models import Vehicle, Model, Driver
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone
from zoneinfo import ZoneInfo
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from taxi_manager.geo_tracking.models import VehicleLocation


class VehileLocationSerializerGeoJson(GeoFeatureModelSerializer):
    class Meta:
        model = VehicleLocation
        geo_field = "location"
        fields = (
            "id",
            "tracked_at",
        )

    def to_representation(self, instance):
        self.fields["tracked_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        return super().to_representation(instance)


class VehileLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLocation
        fields = (
            "id",
            "location",
            "tracked_at",
        )

    def to_representation(self, instance):
        self.fields["tracked_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        return super().to_representation(instance)


class VehicleReadSerializer(serializers.ModelSerializer):
    model_id = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    active_driver_id = serializers.IntegerField()
    color = serializers.CharField()
    model__name = serializers.CharField(source="model.name")
    enterprise_id = serializers.SerializerMethodField()
    # model_name = serializers.SerializerMethodField()
    # model = ModelSerializer()

    def get_model_id(self, obj):
        return obj.model.id
    
    def get_display_name(self, obj):
        return f"{obj.model.name} {obj.number}"    


    def get_enterprise_id(self, obj):
        if not obj.enterprise:
            return None
        return obj.enterprise.id

    def to_representation(self, instance):
        self.fields["purchased_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.enterprise.time_zone.code)
        )

        representation = super().to_representation(instance)
        representation["driver_ids"] = representation.pop("drivers")

        # representation["enterprise_id"] = representation.pop("enterprise")

        # if not representation["active_driver_id"]:
        #     representation["active_driver_id"] = -1

        return representation

    class Meta:
        # depth = 1
        model = Vehicle
        fields = (
            "id",
            "display_name",
            "model_id",
            "color",
            "number",
            "vin",
            "year_of_manufacture",
            "mileage",
            "price",
            # "enterprise_id",
            "drivers",
            "active_driver_id",
            "model__name",
            "enterprise_id",
            "purchased_at",
        )


class VehicleWriteSerializer(serializers.ModelSerializer):
    enterprise_id = serializers.PrimaryKeyRelatedField(
        source="enterprise", queryset=Enterprise.objects.all()
    )

    model_id = serializers.PrimaryKeyRelatedField(
        source="model", queryset=Model.objects.all()
    )

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "model_id",
            "number",
            "vin",
            "year_of_manufacture",
            "mileage",
            "price",
            "enterprise_id",
            "purchased_at",
        )


class ModelSerializer(serializers.ModelSerializer):
    type_code = serializers.SerializerMethodField()
    # type_name = serializers.SerializerMethodField()

    def get_type_code(self, obj):
        return obj.type

    # def get_type_name(self,obj):
    #     return obj.get_type_display()

    class Meta:
        model = Model
        fields = (
            "id",
            "name",
            "color",
            "type_code",
            "number_of_seats",
            "tank_capacity_l",
            "load_capacity_kg",
            "created_at",
            "updated_at",
        )


class EnterpriseSerializer(serializers.ModelSerializer):
    time_zone_code = serializers.CharField(source="time_zone.code", read_only=True)

    class Meta:
        model = Enterprise

        fields = ("id", "name", "city", "time_zone", "time_zone_code")


class DriverSerializer(serializers.ModelSerializer):
    # enterprise_id = serializers.SerializerMethodField()

    # def get_enterprise_id(self, obj):
    #     return obj.enterprise.id

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation["vehicle_ids"] = representation.pop("vehicles")
    #     return representation

    class Meta:
        model = Driver

        fields = (
            "id",
            "first_name",
            "last_name",
            # "enterprise_id",
            # "vehicles",
        )


class TimeZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeZone

        fields = (
            "id",
            "code",
            "utc_offset",
            "display_name",
        )



    


