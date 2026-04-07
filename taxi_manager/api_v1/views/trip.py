from taxi_manager.vehicle.models import Vehicle
from taxi_manager.enterprise.models import Enterprise

from taxi_manager.geo_tracking.models import VehicleLocation, Trip
from taxi_manager.geocoding.models import GeoAddress

from taxi_manager.exchange.services import EnterprisePeriodExchangeService

from ..serializers.trip import (
    TripPointSerializer,
    TripSerializer,
    TripPointSerializerGeoJSON,
)

from django.shortcuts import get_object_or_404

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.db.models import PointField, MakeLine,  GeometryField

from rest_framework import generics, parsers, views, response

from django.db.models import OuterRef, Subquery, F, Q, ExpressionWrapper
from django.db.models.functions import Cast

from django.http import FileResponse

from zipfile import ZipFile, ZIP_DEFLATED
import json
import io

from datetime import datetime


class TripPointListAPIView(generics.ListAPIView):
    def get_serializer_class(self):
        response_format = self.request.query_params.get("response_format")

        if response_format == "geojson":
            return TripPointSerializerGeoJSON

        return TripPointSerializer


    def get_queryset(self):
        vehicle_id = self.kwargs.get("vehicle_id")
        vehicle = Vehicle.objects.get(pk=vehicle_id)

        filter_data_from = None
        if self.request.query_params.get("from"):
            filter_data_from = datetime.fromisoformat(
                self.request.query_params.get("from").replace("Z", "+00:00")
            )

        filter_data_to = None
        if self.request.query_params.get("to"):
            filter_data_to = datetime.fromisoformat(
                self.request.query_params.get("to").replace("Z", "+00:00")
            )

        queryset = Trip.objects.filter(vehicle=vehicle)

        if filter_data_from:
            queryset = queryset.filter(started_at__gte=filter_data_from)

        if filter_data_to:
            queryset = queryset.filter(ended_at__lte=filter_data_to)

        return queryset.annotate_path()


class TripListAPIView(generics.ListAPIView):
    serializer_class = TripSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs.get("vehicle_id")

        filter_data_from = None
        if self.request.query_params.get("from"):
            filter_data_from = datetime.fromisoformat(
                self.request.query_params.get("from").replace("Z", "+00:00")
            )

        filter_data_to = None
        if self.request.query_params.get("to"):
            filter_data_to = datetime.fromisoformat(
                self.request.query_params.get("to").replace("Z", "+00:00")
            )


        vehicle = Vehicle.objects.get(pk=vehicle_id)

        queryset = vehicle.trips.all()

        if filter_data_from:
            queryset = queryset.filter(started_at__gte=filter_data_from)

        if filter_data_to:
            queryset = queryset.filter(ended_at__lte=filter_data_to)

        points = (
            VehicleLocation.objects.filter(vehicle=vehicle)
            .filter(
                tracked_at__gte=OuterRef("started_at"),
                tracked_at__lt=OuterRef("ended_at"),
            )
            .values("location")
        )

        start_address = GeoAddress.objects.filter(
            area__covers=OuterRef("start_point")
        ).values("display_name")[:1]
        end_address = GeoAddress.objects.filter(
            area__covers=OuterRef("end_point")
        ).values("display_name")[:1]

        radius_search_m = 150
        start_point_ref = ExpressionWrapper(
            OuterRef("start_point"),
            output_field=PointField(srid=4326, geography=True),
        )
        end_point_ref = ExpressionWrapper(
            OuterRef("end_point"),
            output_field=PointField(srid=4326, geography=True),
        )
        near_start_address = (
            GeoAddress.objects.filter(
                area__dwithin=(OuterRef("start_point"), radius_search_m)
            )
            .annotate(distance=Distance("area", start_point_ref))
            .order_by("distance")
        )
        near_end_address = (
            GeoAddress.objects.filter(
                area__dwithin=(OuterRef("end_point"), radius_search_m)
            )
            .annotate(distance=Distance("area", end_point_ref))
            .order_by("distance")
        )

        queryset = (
            queryset.annotate(
                start_point=Subquery(points.order_by("tracked_at")[:1]),
                end_point=Subquery(points.order_by("-tracked_at")[:1]),
            )
            .annotate(
                start_address=Subquery(start_address),
                end_address=Subquery(end_address),
            )
            .annotate(
                near_start_address=Subquery(
                    near_start_address.values("display_name")[:1]
                ),
                near_end_address=Subquery(near_end_address.values("display_name")[:1]),
                near_start_address_distance=Subquery(
                    near_start_address.values("distance")[:1]
                ),
                near_end_address_distance=Subquery(
                    near_end_address.values("distance")[:1]
                ),
            )
        )

        return queryset

    def list(self, request, *args, **kwargs):
        point_need_load_address = []
        point_need_load_address.extend(
            [v.start_point for v in self.get_queryset() if v.start_address is None]
        )
        point_need_load_address.extend(
            [v.end_point for v in self.get_queryset() if v.end_address is None]
        )

        GeoAddress.load_address_for_points(point_need_load_address)

        return super().list(request, *args, **kwargs)


def export_enterprise_trip_archive(request,enterprise_id):
    service = EnterprisePeriodExchangeService()

    date_from = datetime.fromisoformat(request.GET.get("from", None))
    date_to = datetime.fromisoformat(request.GET.get("to", None))
    print(enterprise_id, "enterprise_id")
    enterprise = get_object_or_404(Enterprise, pk=enterprise_id)


    archive = service.export_archive(enterprise, date_from, date_to)
 
    filename = service.get_filename(enterprise, date_from, date_to)

    return FileResponse(archive, filename=filename, content_type="application/zip", as_attachment=True)


class ImportEnterpriseTripArchiveView(views.APIView):
    parser_classes = [parsers.FileUploadParser]

    def put(self, request, enterprise_id, filename, format=None):
        print("начало загрузки")
        get_object_or_404(Enterprise, pk=enterprise_id)

        file_obj = request.data["file"]

        service = EnterprisePeriodExchangeService()
        service.import_archive(io.BytesIO(file_obj.read())) 
            
        print("Окончание загрузки")
        return response.Response(status=204)
    












