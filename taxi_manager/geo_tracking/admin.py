from django.contrib.gis import admin

from .models import VehicleLocation

class VehicleLocationAdmin(admin.GISModelAdmin):
    autocomplete_fields = ("vehicle",)
    list_display = (
        "id",
        "vehicle",
        "location",
        "tracked_at",
    )

admin.site.register(VehicleLocation, VehicleLocationAdmin)
