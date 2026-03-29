from rest_framework import generics, viewsets, filters

from taxi_manager.vehicle.models import Vehicle, Model, Driver, VehicleDriver
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone
from taxi_manager.geo_tracking.models import VehicleLocation, Trip
from taxi_manager.geocoding.models import GeoAddress

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.db.models import PointField

from .serializers import (
    VehicleReadSerializer,
    VehicleWriteSerializer,
    ModelSerializer,
    DriverSerializer,
    EnterpriseSerializer,
    TimeZoneSerializer,
    VehileLocationSerializerGeoJson,
    VehileLocationSerializer,
    TripPointSerializer,
    TripSerializer,
    TripPointSerializerGeoJSON,
)
from django.db.models import OuterRef, Subquery, F, Q, ExpressionWrapper
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from django.db.models.deletion import RestrictedError
from .exceptions import DeletionConflict

from datetime import datetime

User = get_user_model()


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleReadSerializer
    queryset = Vehicle.objects.all()
    # filter_backends = [filters.OrderingFilter]

    http_method_names = ["get", "put", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("Авторизуйтесь")

        active_driver = VehicleDriver.objects.filter(
            active=True, vehicle=OuterRef("pk")
        ).values("driver")[:1]

        vehicles = Vehicle.objects

        driver_id = self.kwargs.get("driver_id")
        if driver_id:
            vehicles = Driver.objects.get(id=driver_id).vehicles

        enterprise_id = self.kwargs.get("enterprise_id")
        if enterprise_id:
            vehicles = vehicles.filter(enterprise=enterprise_id)

        enterprise_ids = user.managed_enterprises.values("id")
        vehicles = vehicles.filter(enterprise__in=enterprise_ids)

        vehicles = vehicles.prefetch_related("model").select_related(
            "enterprise__time_zone"
        )

        return vehicles.annotate(
            active_driver_id=Subquery(active_driver), color=F("model__color")
        ).all()

    def get_object(self):
        pk = self.kwargs["pk"]

        get_object_or_404(Vehicle, pk=pk)

        try:
            perm_obj = self.get_queryset().get(pk=pk)
        except Vehicle.DoesNotExist:
            raise PermissionDenied("У вас нет прав менеджера на это авто")

        return perm_obj

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("Авторизуйтесь", code="111")

        if not user.managed_enterprises.filter(
            id=self.request.data["enterprise_id"]
        ).exists():
            raise PermissionDenied(
                "Вы можете добавлять авто только по своему предприятию"
            )

        return super().perform_create(serializer)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("Авторизуйтесь")

        if not user.managed_enterprises.filter(
            id=self.request.data["enterprise_id"]
        ).exists():
            raise PermissionDenied("Вы можете устанавливать только свое предприятие")

        return super().update(request, *args, **kwargs)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in SAFE_METHODS:
            return VehicleReadSerializer
        return VehicleWriteSerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated("Авторизуйтесь")

        if not user.managed_enterprises.exists():
            raise PermissionDenied(
                "Список авто могут просматривать только авторизованные пользователи"
            )

        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except RestrictedError as e:
            raise DeletionConflict(str(e))

    # @action(detail=False, methods=["GET"], url_path="TEST", url_name="TTTTEST")
    # def vehicles_of_driver(self, request):
    #     print("vehicles_of_driver(self, request):")


class ModelListAPIView(generics.ListAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


class ModelDetailAPIView(generics.RetrieveAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


class EnterpriseListAPIView(generics.ListAPIView):
    serializer_class = EnterpriseSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            raise NotAuthenticated("Авторизуйтесь")

        return user.managed_enterprises.all()


class EnterpriseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer

    def get_object(self):
        pk = self.kwargs["pk"]
        user = self.request.user

        obj = get_object_or_404(Enterprise, pk=pk)

        if user.is_superuser:
            return obj

        try:
            perm_obj = user.managed_enterprises.get(pk=pk)
        except Enterprise.DoesNotExist:
            raise PermissionDenied(
                f'У вас нет прав менеджера в "{obj.name}"(id={obj.id})'
            )

        if perm_obj:
            return perm_obj


class DriverListAPIView(generics.ListAPIView):
    serializer_class = DriverSerializer

    filterset_fields = {
        "id": ["exact", "in"],
    }

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("Авторизуйтесь")

        drivers = Driver.objects

        if not user.is_superuser:
            enterprise_ids = user.managed_enterprises.values("id")
            drivers = drivers.filter(enterprise__in=enterprise_ids)

        enterprise_id = self.kwargs.get("enterprise_id")
        if enterprise_id:
            drivers = drivers.filter(enterprise=enterprise_id)

        return drivers.all()


class DriverDetailAPIView(generics.RetrieveAPIView):
    serializer_class = DriverSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            raise PermissionDenied("Авторизуйтесь")

        drivers = Driver.objects
        if not user.is_superuser:
            enterprise_ids = user.managed_enterprises.values("id")
            drivers = drivers.filter(enterprise__in=enterprise_ids)

        return drivers

    def get_object(self):
        pk = self.kwargs["pk"]

        get_object_or_404(Driver, pk=pk)

        try:
            perm_obj = self.get_queryset().get(pk=pk)
        except Driver.DoesNotExist:
            raise PermissionDenied("Этот водитель не в вашей организации")

        return perm_obj


class SessionLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out"}, status=200)


class TimeZoneListAPIView(generics.ListAPIView):
    queryset = TimeZone.objects.all()
    serializer_class = TimeZoneSerializer


class VehicleLocationListAPIView(generics.ListAPIView):
    def get_queryset(self):
        vehicle_id = self.kwargs["vehicle_id"]

        get_object_or_404(Vehicle, pk=vehicle_id)

        _queryset = VehicleLocation.objects.filter(vehicle=vehicle_id).select_related(
            "vehicle__enterprise__time_zone"
        )

        _queryset = _queryset.order_by("-id").filter(tracked_at__lte=timezone.now())

        return _queryset

    def get_serializer_class(self):
        response_format = self.request.query_params.get("response_format")

        if response_format == "geojson":
            return VehileLocationSerializerGeoJson

        return VehileLocationSerializer


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
        print(filter_data_from)
        filter_data_to = None
        if self.request.query_params.get("to"):
            filter_data_from = datetime.fromisoformat(
                self.request.query_params.get("from").replace("Z", "+00:00")
            )

        trip = Trip.objects.filter(vehicle=vehicle).filter(
                started_at__lte=OuterRef("tracked_at"),
                ended_at__gt=OuterRef("tracked_at"),
            )
        
        if filter_data_from:
            trip = trip.filter(started_at__gte=filter_data_from)

        if filter_data_to:
            trip = trip.filter(ended_at__lte=filter_data_to)

        trip = trip.values("id")[:1]

        queryset = (
            VehicleLocation.objects.filter(
                vehicle=vehicle
            )
            .annotate(trip=Subquery(trip))
            .filter(trip__isnull=False)
        )

        if filter_data_from:
            queryset = queryset.filter(tracked_at__gte=filter_data_from)

        if filter_data_to:
            queryset = queryset.filter(tracked_at__lt=filter_data_to)   

        return queryset


class TripListAPIView(generics.ListAPIView):
    serializer_class = TripSerializer

    def get_queryset(self):
        vehicle_id = self.kwargs.get("vehicle_id")
        vehicle = Vehicle.objects.get(pk=vehicle_id)

        queryset = vehicle.trips.all()

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
