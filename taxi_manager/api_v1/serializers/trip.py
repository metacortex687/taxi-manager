from rest_framework import serializers
from zoneinfo import ZoneInfo
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from taxi_manager.geo_tracking.models import VehicleLocation

class TripPointSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    trip = serializers.IntegerField(read_only=True)
    tracked_at = serializers.DateTimeField(read_only=True)
    location = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        self.fields["tracked_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        return super().to_representation(instance)

class TripPointSerializerGeoJSON(GeoFeatureModelSerializer):
    trip = serializers.IntegerField(read_only=True)
    route = GeometrySerializerMethodField()

    def get_route(self, obj):
        return obj["route"]
    
    # def to_representation(self, instance):
    #     self.fields["tracked_at"] = serializers.DateTimeField(
    #         default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
    #     )
    #     return super().to_representation(instance)
    
    class Meta:
        model = VehicleLocation
        geo_field = "route"
        fields = (
            "trip",
        )
    


class TripSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)    
    start_point = serializers.SerializerMethodField(read_only=True)
    ended_at = serializers.DateTimeField(read_only=True)
    end_point = serializers.SerializerMethodField(read_only=True)

    def to_representation(self, instance):
        self.fields["started_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        self.fields["ended_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        return super().to_representation(instance)

    def get_start_point(self, obj):
        address = obj.start_address
        if address is None and obj.near_start_address is not None:
            address = f"(~{round(obj.near_start_address_distance.m)} м) {obj.near_start_address}"


        return {
            "lat": obj.start_point.y,
            "lon": obj.start_point.x,
            "address": address,
        }

    def get_end_point(self, obj):
        address = obj.end_address
        if address is None and obj.near_end_address is not None:
            address = f"(~{round(obj.near_end_address_distance.m)} м) {obj.near_end_address}"

        return {
            "lat": obj.end_point.y,
            "lon": obj.end_point.x,
            "address": address,
        }