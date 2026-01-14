from django.contrib import admin

from .models import Vehicle, Model, Driver, VehicleDriver


class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "enterprise",
        "model",
        "number",
        "vin",
        "year_of_manufacture",
        "mileage",
        "price",
    )

    fields = (
        "model",
        "number",
        "vin",
        "year_of_manufacture",
        "mileage",
        "price",
        "enterprise",
    )

    list_select_related = ["enterprise"]


class ModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "type",
        "number_of_seats",
        "tank_capacity_l",
        "load_capacity_kg",
    )

class VehicleDriverAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "driver",
        "vehicle",
        "active",
    )

    list_filter = (
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


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Model, ModelAdmin)

admin.site.register(Driver, DriverAdmin)
admin.site.register(VehicleDriver, VehicleDriverAdmin)