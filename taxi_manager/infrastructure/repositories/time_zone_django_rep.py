from taxi_manager.application.time_zone.time_zone_repository import (
    ITimeZoneRepository,
)

from taxi_manager.domain.entities.time_zone import TimeZone, TimeZoneId

from taxi_manager.infrastructure.time_zones.models import TimeZone as TimeZoneOrm


class TimeZoneDjangoRep(ITimeZoneRepository):
    def get_list(self, timezone_ids: list[TimeZoneId]) -> list[TimeZone]:
        orm_objects = TimeZoneOrm.objects.filter(
            id__in=[tz.value for tz in timezone_ids]
        ).values("id", "code", "utc_offset")

        return [
            TimeZone(
                id=TimeZoneId(obj["id"]), code=obj["code"], utc_offset=obj["utc_offset"]
            )
            for obj in orm_objects
        ]

    def get(self, time_zone_id: TimeZoneId) -> TimeZone:
        obj = TimeZoneOrm.objects.get(pk=time_zone_id.value)

        return TimeZone(id=TimeZoneId(obj.id), code=obj.code, utc_offset=obj.utc_offset)
