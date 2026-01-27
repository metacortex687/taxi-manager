from rest_framework import generics, viewsets
from ..vehicle.models import Vehicle, Model, Driver, VehicleDriver
from ..enterprise.models import Enterprise
from .serializers import (
    VehicleReadSerializer,
    VehicleWriteSerializer,
    ModelSerializer,
    DriverSerializer,
    EnterpriseSerializer,
)
from django.db.models import OuterRef, Subquery, F
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS

User = get_user_model()


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleReadSerializer
    queryset = Vehicle.objects.all()

    http_method_names = ["get", "put", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("Авторизуйтесь")

        active_driver = VehicleDriver.objects.filter(
            active=True, vehicle=OuterRef("pk")
        ).values("driver")[:1]

        vehicles = Vehicle.objects

        driver_id = self.kwargs.get("driver_id")
        if driver_id:
            vehicles = Driver.objects.get(id=driver_id).vehicles


        enterprise_ids = user.managed_enterprises.values("id")
        vehicles = vehicles.filter(enterprise__in=enterprise_ids)

        return vehicles.annotate(active_driver_id=Subquery(active_driver)).all()

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
            raise PermissionDenied("Авторизуйтесь")

        if not user.managed_enterprises.filter(
            id=self.request.data["enterprise"]
        ).exists():
            raise PermissionDenied(
                "Вы можете добавлять авто только по своему предприятию"
            )

        return super().perform_create(serializer)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("Авторизуйтесь")

        if not user.managed_enterprises.filter(
            id=self.request.data["enterprise"]
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
            raise PermissionDenied("Авторизуйтесь")

        if not user.managed_enterprises.exists():
            raise PermissionDenied(
                "Список авто могут просматривать только авторизованные пользователи"
            )

        return super().list(request, *args, **kwargs)

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
        if user.is_superuser:
            return Enterprise.objects.all()

        return user.managed_enterprises.all()


class EnterpriseDetailAPIView(generics.RetrieveAPIView):
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

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            raise PermissionDenied("Авторизуйтесь")

        drivers = Driver.objects

        if not user.is_superuser:
            enterprise_ids = user.managed_enterprises.values("id")
            drivers = drivers.filter(enterprise__in=enterprise_ids)

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
