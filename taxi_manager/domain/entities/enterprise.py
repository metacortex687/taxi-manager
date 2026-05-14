from .manager import ManagerId

from .time_zone import TimeZoneId

from dataclasses import dataclass


@dataclass(frozen=True)
class EnterpriseId:
    value: int


@dataclass
class Enterprise:
    id: EnterpriseId
    name: str
    city: str
    time_zone_id: TimeZoneId  # TODO time_zone_id
