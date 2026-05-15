from taxi_manager.application.dto.enterprise_dto import EnterpriseDTO
from taxi_manager.application.repositories.enterprise_rep import EnterpriseRepInterface
from taxi_manager.application.repositories.time_zone_rep import TimeZoneRepInterface
from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId


class EnterpriseUseCase:
    def __init__(
        self,
        enterprise_rep: EnterpriseRepInterface,
        time_zone_rep: TimeZoneRepInterface,
    ):
        self.enterprise_rep = enterprise_rep
        self.time_zone_rep = time_zone_rep

    def get(self, enterprise_id: EnterpriseId) -> EnterpriseDTO:
        enterprise = self.enterprise_rep.get(enterprise_id)
        time_zone = self.time_zone_rep.get(enterprise.time_zone_id)

        return EnterpriseDTO.from_entity_and_timezone(enterprise, time_zone)

    def update(self, enterprise: Enterprise):
        self.enterprise_rep.update(enterprise)

        