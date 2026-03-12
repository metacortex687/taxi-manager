from rest_framework import serializers
from ..vehicle.models import Vehicle, Model, Driver
from ..enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

class VehicleReadSerializer(serializers.ModelSerializer):
    model_id = serializers.SerializerMethodField()
    active_driver_id = serializers.IntegerField()
    color = serializers.CharField()
    model__name = serializers.CharField(source="model.name")
    enterprise_id = serializers.SerializerMethodField()
    # model_name = serializers.SerializerMethodField()
    # model = ModelSerializer()

    def get_model_id(self, obj):
        return obj.model.id

    def get_enterprise_id(self, obj):
        if not obj.enterprise:
            return None
        return obj.enterprise.id

    def to_representation(self, instance):
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
        )

class VehicleWriteSerializer(serializers.ModelSerializer):
    enterprise_id = serializers.PrimaryKeyRelatedField(
        source="enterprise",
        queryset=Enterprise.objects.all()
    )

    model_id = serializers.PrimaryKeyRelatedField(
        source="model",
        queryset=Model.objects.all()
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
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation["vehicle_ids"] = representation.pop("vehicles")
    #     representation["driver_ids"] = representation.pop("drivers")
    #     return representation

    class Meta:
        model = Enterprise

        fields = ("id", "name", "city","time_zone")


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