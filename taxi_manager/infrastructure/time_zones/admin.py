from django.contrib import admin

from .models import TimeZone
# Register your models here.

class TimeZoneAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "code",
        "utc_offset",
        "display_name",
    )

admin.site.register(TimeZone, TimeZoneAdmin)

