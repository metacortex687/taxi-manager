
from taxi_manager.exchange import resources

from .models import Vehicle, Model, Driver, VehicleDriver

from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

class VehicleAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "model",
        "number",
        "enterprise",
        "vin",
        "year_of_manufacture",
        "mileage",
        "price",
        "purchased_at",
    )

    fields = (
        "model",
        "number",
        "vin",
        "year_of_manufacture",
        "mileage",
        "price",
        "enterprise",
        "purchased_at",
    )

    list_select_related = ["enterprise"]
    search_fields = ["=id"]
    resource_classes = [resources.VehicleResource]


class ModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "color",
        "type",
        "number_of_seats",
        "tank_capacity_l",
        "load_capacity_kg",
    )


class VehicleDriverAdmin(admin.ModelAdmin):


    list_display = (
        "id",
        "enterprise",
        "driver",
        "vehicle",
        "active",
    )

    list_filter = (
        "enterprise",
        "driver",
        "vehicle",
    )


class DriverAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "TIN",
        "enterprise",
    )

    list_select_related = ["enterprise"]
    search_fields = ["number", "vin"] 


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Model, ModelAdmin)

admin.site.register(Driver, DriverAdmin)
admin.site.register(VehicleDriver, VehicleDriverAdmin)