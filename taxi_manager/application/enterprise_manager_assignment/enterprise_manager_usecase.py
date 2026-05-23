

from taxi_manager.application.enterprise.dto import EnterpriseDTO
from taxi_manager.application.enterprise_manager_assignment.repository import IEnterpriseManagerAssignmentRepository
from taxi_manager.application.time_zone.repository import ITimeZoneRepository

from ...domain.entities.enterprise import EnterpriseId

from ...domain.entities.manager import ManagerId




class EnterpriseManagerUseCase:
    def __init__(
        self,
        enterprise_manager_assigment_rep: IEnterpriseManagerAssignmentRepository,
        time_zone_rep: ITimeZoneRepository,
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

    def delete(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        return self.enterprise_manager_assigment_rep.delete(enterprise_id, manager_id)

    def is_assignment_exist(
        self, enterprise_id: EnterpriseId, manager_id: ManagerId
    ) -> bool:
        return self.enterprise_manager_assigment_rep.is_assignment_exist(
            enterprise_id,
            manager_id,
        )
