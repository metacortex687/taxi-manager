from rest_framework import generics
from ..vehicle.models import Vehicle, Model, Driver, VehicleDriver
from ..enterprise.models import Enterprise
from .serializers import (
    VehicleSerializer,
    ModelSerializer,
    DriverSerializer,
    EnterpriseSerializer,
)
from django.db.models import OuterRef, Subquery, F
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


class VehicleListAPIView(generics.ListAPIView):
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

        if not user.is_superuser:
            enterprise_ids = user.managed_enterprises.values("id")
            vehicles = vehicles.filter(enterprise__in=enterprise_ids)

        return vehicles.annotate(active_driver_id=Subquery(active_driver)).all()

    serializer_class = VehicleSerializer


class VehicleDetailAPIView(generics.RetrieveAPIView):
    serializer_class = VehicleSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            raise PermissionDenied("Авторизуйтесь")

        active_driver = VehicleDriver.objects.filter(
            active=True, vehicle=OuterRef("pk")
        ).values("driver")[:1]

        vehicles = Vehicle.objects
        if not user.is_superuser:
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
                f'У вас нет прав менеджера на "{obj.name}"(id={obj.id})'
            )

        if perm_obj:
            return perm_obj


class DriverListAPIView(generics.ListAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class DriverDetailAPIView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
