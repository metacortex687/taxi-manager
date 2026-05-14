from dataclasses import dataclass

from taxi_manager.domain.entities.enterprise import Enterprise
from taxi_manager.domain.entities.time_zone import TimeZone


@dataclass(frozen=True)
class EnterpriseDTO:
    id: int
    name: str
    city: str
    time_zone: int  # TODO  time_zone_id
    time_zone_code: str

    @classmethod
    def from_entity_and_timezone(cls, enterprise: Enterprise, time_zone: TimeZone):
        return cls(
            id=enterprise.id.value,
            name=enterprise.name,
            city=enterprise.city,
            time_zone=enterprise.time_zone.value,
            time_zone_code=time_zone.code,
        )
