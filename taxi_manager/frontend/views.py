from django.shortcuts import render, get_object_or_404
from taxi_manager.enterprise.models import Enterprise


def vehicles(request, pk):
    return render(
        request, "vehicles.html", {"enterprise": get_object_or_404(Enterprise, pk=pk)}
    )


# Create your views here.
