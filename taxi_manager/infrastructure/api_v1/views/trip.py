from taxi_manager.infrastructure.observability.tracing import trace_span
from taxi_manager.infrastructure.vehicle.models import Vehicle
from taxi_manager.infrastructure.enterprise.models import Enterprise

from taxi_manager.infrastructure.geo_tracking.models import VehicleLocation, Trip
from taxi_manager.infrastructure.geocoding.models import GeoAddress

from taxi_manager.infrastructure.geocoding import tasks as geocoding_tasks

from taxi_manager.infrastructure.exchange.services import (
    EnterprisePeriodExchangeService,
)

from ..serializers.trip import (
    TripPointSerializer,
    TripPointSerializerGeoJSONFast,
    TripSerializer,
    TripPointSerializerGeoJSON,
)

from django.shortcuts import get_object_or_404

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.db.models import PointField, MakeLine, GeometryField

from rest_framework import generics, parsers, views, response

from django.db.models import OuterRef, Subquery, F, Q, ExpressionWrapper
from django.db.models.functions import Cast

from django.http import FileResponse

from rest_framework.response import Response

from zipfile import ZipFile, ZIP_DEFLATED
import json
import io

from datetime import datetime


class TripPointListAPIView(generics.ListAPIView):
    filterset_fields = ["id"]
    pagination_class = None

    def get_serializer_class(self):
        response_format = self.request.query_params.get("response_format")

        if response_format == "geojson":
            return TripPointSerializerGeoJSON
        
        if response_format == "geojson_fast":
            return TripPointSerializerGeoJSONFast

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

        response_format = self.request.query_params.get("response_format")

        if response_format == "geojson_fast":
            return queryset.annotate_geojson_feature()

        return queryset.annotate_path()
    
    def list(self, request, *args, **kwargs):
        with trace_span(
            "TripPointListAPIView.list",
            stage="view",
            attrs={
                "vehicle_id": kwargs.get("vehicle_id"),
                "response_format": request.query_params.get("response_format", ""),
                "trip_id": request.query_params.get("id", ""),
            },
        ):
            with trace_span("TripPointListAPIView.get_queryset", stage="view"):
                queryset = self.filter_queryset(self.get_queryset())

            response_format = request.query_params.get("response_format")

            if response_format == "geojson_fast":
                with trace_span(
                    "TripPointListAPIView.geojson_fast_values",
                    stage="db_fetch",
                ):
                    features = list(
                        queryset.values_list("geojson_feature", flat=True)
                    )

                with trace_span(
                    "TripPointListAPIView.rows_count",
                    stage="debug",
                    attrs={"rows.count": len(features)},
                ):
                    pass

                with trace_span("TripPointListAPIView.response_create", stage="response"):
                    return Response({
                        "results": {
                            "type": "FeatureCollection",
                            "features": features,
                        }
                    })

            with trace_span("TripPointListAPIView.queryset_evaluate", stage="db_fetch"):
                rows = list(queryset)

            with trace_span(
                "TripPointListAPIView.rows_count",
                stage="debug",
                attrs={"rows.count": len(rows)},
            ):
                pass

            with trace_span("TripPointListAPIView.serializer_init", stage="serialize"):
                serializer = self.get_serializer(rows, many=True)

            with trace_span("TripPointListAPIView.serializer_data", stage="serialize"):
                data = serializer.data

            with trace_span("TripPointListAPIView.response_create", stage="response"):
                return Response({"results": data})

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
        for trip in self.get_queryset():
            if trip.start_point is not None and trip.start_address is None:
                point_need_load_address.append(
                    {
                        "lon": trip.start_point.x,
                        "lat": trip.start_point.y,
                    }
                )

            if trip.end_point is not None and trip.end_address is None:
                point_need_load_address.append(
                    {
                        "lon": trip.end_point.x,
                        "lat": trip.end_point.y,
                    }
                )

        if point_need_load_address:
            geocoding_tasks.load_geo_addresses.enqueue(point_need_load_address)

        return super().list(request, *args, **kwargs)


def export_enterprise_trip_archive(request, enterprise_id):
    service = EnterprisePeriodExchangeService()

    date_from = datetime.fromisoformat(request.GET.get("from", None))
    date_to = datetime.fromisoformat(request.GET.get("to", None))
    print(enterprise_id, "enterprise_id")
    enterprise = get_object_or_404(Enterprise, pk=enterprise_id)

    archive = service.export_archive(enterprise, date_from, date_to)

    filename = service.get_filename(enterprise, date_from, date_to)

    return FileResponse(
        archive, filename=filename, content_type="application/zip", as_attachment=True
    )


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
