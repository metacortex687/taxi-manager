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


class VehicleListAPIView(generics.ListCreateAPIView):
    def get_queryset(self):
        active_driver = VehicleDriver.objects.filter(
            active=True, vehicle=OuterRef("pk")
        ).values("driver")[:1]

        vehicles = Vehicle.objects

        driver_id = self.kwargs.get("driver_id")
        if driver_id:
            vehicles =  Driver.objects.get(id=driver_id).vehicles

        return vehicles.annotate(active_driver_id=Subquery(active_driver)).all()

    serializer_class = VehicleSerializer


class VehicleDetailAPIView(generics.RetrieveAPIView):
    def get_queryset(self):
        active_driver = VehicleDriver.objects.filter(active=True, vehicle=OuterRef("pk")).values("driver")[:1]
        return Vehicle.objects.annotate(active_driver_id=Subquery(active_driver)).all()
    
    serializer_class = VehicleSerializer


class ModelListAPIView(generics.ListCreateAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


class ModelDetailAPIView(generics.RetrieveAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer


class EnterpriseListAPIView(generics.ListCreateAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer


class EnterpriseDetailAPIView(generics.RetrieveAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer


class DriverListAPIView(generics.ListCreateAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class DriverDetailAPIView(generics.RetrieveAPIView):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer