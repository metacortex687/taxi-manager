from django.contrib.gis import admin

from .models import VehicleLocation

class VehicleLocationAdmin(admin.GISModelAdmin):
    autocomplete_fields = ("vehicle",)

admin.site.register(VehicleLocation, VehicleLocationAdmin)
