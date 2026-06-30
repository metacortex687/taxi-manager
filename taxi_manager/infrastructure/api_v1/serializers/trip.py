import json

from rest_framework import serializers
from zoneinfo import ZoneInfo
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from taxi_manager.infrastructure.api_v1.serializers.trace import TracedGeometrySerializerMethodField
from taxi_manager.infrastructure.geo_tracking.models import VehicleLocation, Trip
from taxi_manager.infrastructure.observability.tracing import trace_method


class TripPointSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    trip = serializers.IntegerField(read_only=True)
    tracked_at = serializers.DateTimeField(read_only=True)
    location = serializers.CharField(read_only=True)

    @trace_method("TripPointSerializer.to_representation")
    def to_representation(self, instance):
        self.fields["tracked_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        return super().to_representation(instance)


class TripPointSerializerGeoJSON(GeoFeatureModelSerializer):
    trip = serializers.IntegerField(source="id", read_only=True)
    route = TracedGeometrySerializerMethodField(
        span_name="TripPointSerializerGeoJSON.route.to_representation",
        stage="serialize",
    )

    @trace_method("TripPointSerializerGeoJSON.get_route", stage="serialize")
    def get_route(self, obj):
        return obj.path

    @trace_method("TripPointSerializerGeoJSON.to_representation", stage="serialize")
    def to_representation(self, instance):
        return super().to_representation(instance)

    @trace_method("TripPointSerializerGeoJSON.get_properties", stage="serialize")
    def get_properties(self, instance, fields):
        return super().get_properties(instance, fields)

    class Meta:
        model = Trip
        geo_field = "route"
        fields = ("trip",)

class TripPointSerializerGeoJSONFast(serializers.Serializer):
    @trace_method("TripPointSerializerGeoJSONFast.to_representation", stage="serialize")
    def to_representation(self, instance):
        feature = instance.geojson_feature

        if isinstance(feature, str):
            return json.loads(feature)

        return feature


class TripSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    start_point = serializers.SerializerMethodField(read_only=True)
    ended_at = serializers.DateTimeField(read_only=True)
    end_point = serializers.SerializerMethodField(read_only=True)

    @trace_method("TripSerializer.to_representation")
    def to_representation(self, instance):
        self.fields["started_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        self.fields["ended_at"] = serializers.DateTimeField(
            default_timezone=ZoneInfo(instance.vehicle.enterprise.time_zone.code)
        )
        return super().to_representation(instance)

    @trace_method("TripSerializer.get_start_point")
    def get_start_point(self, obj):
        if obj.start_point is None:
            return None

        address = obj.start_address

        if address is None:
            address = "загружается"

        return {
            "lat": obj.start_point.y,
            "lon": obj.start_point.x,
            "address": address,
        }

    def get_end_point(self, obj):
        if obj.end_point is None:
            return None

        address = obj.end_address

        if address is None:
            address = "загружается"

        return {
            "lat": obj.end_point.y,
            "lon": obj.end_point.x,
            "address": address,
        }
