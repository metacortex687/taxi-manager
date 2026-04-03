from django.shortcuts import render, get_object_or_404
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Vehicle


def vehicles(request, pk):
    return render(
        request, "vehicles.html", {"enterprise": get_object_or_404(Enterprise, pk=pk)}
    )

def vehicle_edit(request, pk):
    return render(
        request, "vehicle.html", {"entity": get_object_or_404(Vehicle, pk=pk), "action": "edit"}
    )

def vehicle_new(request):
    return render(
        request, "vehicle.html", {"action": "new"}
    )

def vehicle_trips(request, pk):
    return render(
        request, "vehicle_trips.html", {"entity": get_object_or_404(Vehicle, pk=pk), "action": "view"}
    )

def enterprise_edit(request, pk):
    return render(
        request, "enterprise.html", {"entity": get_object_or_404(Enterprise, pk=pk), "action": "edit"}
    )

def enterprise_export_trips(request, pk):
    return render(
        request, "enterprise_export_trips.html", {"entity": get_object_or_404(Enterprise, pk=pk), "action": "view"}
    )

