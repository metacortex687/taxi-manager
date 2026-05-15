from taxi_manager.application.dto.enterprise_dto import EnterpriseDTO
from taxi_manager.application.repositories.enterprise_repository import (
    IEnterpriseRepository,
)
from taxi_manager.application.repositories.time_zone_repository import ITimeZoneRepository
from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId


class EnterpriseUseCase:
    def __init__(
        self,
        enterprise_rep: IEnterpriseRepository,
        time_zone_rep: ITimeZoneRepository,
    ):
        self.enterprise_rep = enterprise_rep
        self.time_zone_rep = time_zone_rep

    def get(self, enterprise_id: EnterpriseId) -> EnterpriseDTO:
        enterprise = self.enterprise_rep.get(enterprise_id)
        time_zone = self.time_zone_rep.get(enterprise.time_zone_id)

        return EnterpriseDTO.from_entity_and_timezone(enterprise, time_zone)

    def update(self, enterprise: Enterprise):
        self.enterprise_rep.update(enterprise)

    def delete(self, enterprise_id: EnterpriseId):
        self.enterprise_rep.delete(enterprise_id)
