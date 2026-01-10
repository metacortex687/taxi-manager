from rest_framework import generics
from ..vehicle.models import Vehicle
from .serializers import VehicleSerializer

class VehicleListAPIView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.prefetch_related("model").all()
    serializer_class = VehicleSerializer

class VehicleDetailAPIView(generics.RetrieveAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer    

