from rest_framework import generics
from ..vehicle.models import Vehicle, Model, Driver
from ..enterprise.models import Enterprise
from .serializers import (
    VehicleSerializer,
    ModelSerializer,
    DriverSerializer,
    EnterpriseSerializer,
)


class VehicleListAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.prefetch_related("model").all()
    serializer_class = VehicleSerializer


class VehicleDetailAPIView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
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