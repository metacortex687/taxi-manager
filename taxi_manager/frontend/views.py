from django.shortcuts import render, get_object_or_404
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle


def vehicles(request, pk):
    return render(
        request, "vehicles.html", {"enterprise": get_object_or_404(Enterprise, pk=pk)}
    )

def vehicle_edit(request, pk):
    return render(
        request, "vehicle_edit.html", {"vehicle": get_object_or_404(Vehicle, pk=pk)}
    )

def vehicle_new(request):
    return render(
        request, "vehicle_edit.html", {"action": "new"}
    )
# Create your views here.
