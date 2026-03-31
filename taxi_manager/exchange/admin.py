from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone


from import_export import resources


class TimeZoneResource(resources.ModelResource):

    class Meta:
        model = TimeZone

# Register your models here.
