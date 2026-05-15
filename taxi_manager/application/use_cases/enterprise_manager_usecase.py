from taxi_manager.application.repositories.time_zone_rep import (
    TimeZoneRepInterface,
)

from ...domain.entities.enterprise import Enterprise, EnterpriseId

from ...domain.entities.manager import ManagerId

from ..repositories.enterprise_manager_assigment_rep import (
    EnterpriseManagerAssigmentRepInterface,
)
from ..dto.enterprise_dto import EnterpriseDTO


class EnterpriseManagerUseCase:
    def __init__(
        self,
        enterprise_manager_assigment_rep: EnterpriseManagerAssigmentRepInterface,
        time_zone_rep: TimeZoneRepInterface,
    ):
        self.enterprise_manager_assigment_rep = enterprise_manager_assigment_rep
        self.time_zone_repository = time_zone_rep

    def get_manager_assigments(self, manager_id: ManagerId) -> list[EnterpriseDTO]:
        enterprises = self.enterprise_manager_assigment_rep.get_manager_assigments(
            manager_id
        )

        time_zone_ids = [enterprise.time_zone_id for enterprise in enterprises]
        time_zones = self.time_zone_repository.get_list(time_zone_ids)
        time_zones_by_id = {time_zone.id.value: time_zone for time_zone in time_zones}

        return [
            EnterpriseDTO.from_entity_and_timezone(
                enterprise, time_zones_by_id[enterprise.time_zone_id.value]
            )
            for enterprise in enterprises
        ]

    def get_enterprise_assigments(self, enterprise_id: EnterpriseId) -> list[EnterpriseDTO]:
        enterprises = self.enterprise_manager_assigment_rep.get_enterprise_assigments(
            enterprise_id
        )

        time_zone_ids = [enterprise.time_zone_id for enterprise in enterprises]
        time_zones = self.time_zone_repository.get_list(time_zone_ids)
        time_zones_by_id = {time_zone.id.value: time_zone for time_zone in time_zones}

        return [
            EnterpriseDTO.from_entity_and_timezone(
                enterprise, time_zones_by_id[enterprise.time_zone_id.value]
            )
            for enterprise in enterprises
        ]

    def delete(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        return self.enterprise_manager_assigment_rep.delete(
            enterprise_id, manager_id
        )
    
    def is_assigment_exist(self, manager_id: ManagerId, enterprise_id: EnterpriseId)->bool:
        return self.enterprise_manager_assigment_rep.is_assigment_exist(
            manager_id, enterprise_id #TODO enterprise_id, manager_id
        )
