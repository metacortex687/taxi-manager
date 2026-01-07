from django.contrib import admin

from .models import Vehicle, Model, Brand


class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
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
    )


class ModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "brand",
        "name",
        "type",
        "number_of_seats",
        "tank_capacity_l",
        "load_capacity_kg",
    )


class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Vehicle, VehicleAdmin)

admin.site.register(Model, ModelAdmin)
admin.site.register(Brand, BrandAdmin)
