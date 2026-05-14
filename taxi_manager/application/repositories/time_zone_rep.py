from abc import ABC, abstractmethod

from taxi_manager.domain.entities.time_zone import TimeZone, TimeZoneId


class TimeZoneRepInterface(ABC):
    @abstractmethod
    def get_list(self, time_zone_ids: list[TimeZoneId]) -> list[TimeZone]:
        pass
