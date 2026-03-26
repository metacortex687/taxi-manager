from django.contrib.gis import admin

from .models import GeoAddress

class GeoAddressAdmin(admin.GISModelAdmin):
    list_display = (
        "id",
        "display_name",
        "area",
    )

admin.site.register(GeoAddress, GeoAddressAdmin)
# Register your models here.
