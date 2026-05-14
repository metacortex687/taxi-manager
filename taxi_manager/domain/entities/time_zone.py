from dataclasses import dataclass


@dataclass(frozen=True)
class TimeZoneId:
    value: int


@dataclass
class TimeZone:
    id: TimeZoneId
    code: str
    utc_offset: int
