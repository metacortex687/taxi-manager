from rest_framework import generics
from ..vehicle.models import Vehicle, Model
from .serializers import VehicleSerializer, ModelSerializer

class VehicleListAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.prefetch_related("model").all()
    serializer_class = VehicleSerializer

class VehicleDetailAPIView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer    


class ModelDetailAPIView(generics.RetrieveAPIView):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer    