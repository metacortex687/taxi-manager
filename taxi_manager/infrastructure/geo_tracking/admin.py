from django.contrib.gis import admin

from .models import VehicleLocation, Trip

class VehicleLocationAdmin(admin.GISModelAdmin):
    autocomplete_fields = ("vehicle",)
    list_display = (
        "id",
        "vehicle",
        "location",
        "tracked_at",
    )


class TripAdmin(admin.GISModelAdmin):
    autocomplete_fields = ("vehicle",)
    list_display = (
        "id",
        "enterprise",
        "vehicle",
        "started_at",
        "ended_at",
    )

admin.site.register(VehicleLocation, VehicleLocationAdmin)
admin.site.register(Trip, TripAdmin)