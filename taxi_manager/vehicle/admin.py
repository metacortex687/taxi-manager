from django.contrib import admin

from .models import Vehicle


class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "vin",
        "year_of_manufacture",
        "mileage",
        "price",
    )

    fields = (
        "number",
        "vin",
        "year_of_manufacture",
        "mileage",
        "price",
    )


admin.site.register(Vehicle, VehicleAdmin)
