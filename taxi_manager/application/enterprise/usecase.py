from taxi_manager.application.enterprise.commands import (
    DeleteEnterpriseCommand,
    UpdateEnterpriseCommand,
)
from taxi_manager.application.enterprise.dto import EnterpriseDTO
from taxi_manager.application.enterprise.repository import (
    IEnterpriseRepository,
)
from taxi_manager.application.enterprise import results

from taxi_manager.application.enterprise_manager_assignment.repository import (
    IEnterpriseManagerAssignmentRepository,
)
from taxi_manager.application.time_zone.repository import ITimeZoneRepository
from taxi_manager.application.unit_of_work import IUnitOfWork
from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.domain.entities.time_zone import TimeZoneId


class EnterpriseUseCase:
    def __init__(
        self,
        enterprise_repository: IEnterpriseRepository,
        time_zone_repository: ITimeZoneRepository,
        enterprise_manager_repository: IEnterpriseManagerAssignmentRepository,
        unit_of_work: IUnitOfWork,
    ):
        self.enterprise_repository = enterprise_repository
        self.time_zone_repository = time_zone_repository
        self.enterprise_manager_repository = enterprise_manager_repository
        self.unit_of_work = unit_of_work

    def get(self, enterprise_id: EnterpriseId) -> EnterpriseDTO:

        enterprise = self.enterprise_repository.get(enterprise_id)
        time_zone = self.time_zone_repository.get(enterprise.time_zone_id)

        return EnterpriseDTO.from_entity_and_timezone(enterprise, time_zone)

    def get_by_manager(self, enterprise_id_pk, manager_id_pk) -> results.GetEnterpriseDetailResult:
        enterprise_id = EnterpriseId(enterprise_id_pk)
        manager_id = ManagerId(manager_id_pk)

        enterprise = self.enterprise_repository.get(enterprise_id)

        if not self.enterprise_manager_repository.is_assignment_exist(enterprise_id, manager_id):
            return results.GetEnterpriseDetailResult.not_manager(f'У вас нет прав менеджера в "{enterprise.name}"(id={enterprise_id_pk})')        

        time_zone = self.time_zone_repository.get(enterprise.time_zone_id)
        return results.GetEnterpriseDetailResult.received(EnterpriseDTO.from_entity_and_timezone(enterprise, time_zone))

    def update(self, command: UpdateEnterpriseCommand) -> results.UpdateEnterpriseResult:
        enterprise_id = EnterpriseId(command.enterprise_id)
        manager_id = ManagerId(command.manager_id)

        if not self.enterprise_manager_repository.is_assignment_exist(
            enterprise_id=enterprise_id,
            manager_id=manager_id,
        ):
            enterprise = self.enterprise_repository.get(enterprise_id)
            return results.UpdateEnterpriseResult.not_manager(
                f'У вас нет прав менеджера в "{enterprise.name}"(id={enterprise_id.value})'
            )

        updated_enterprise = Enterprise(
            id=enterprise_id,
            name=command.name,
            city=command.city,
            time_zone_id=TimeZoneId(command.time_zone_id),
        )

        self.enterprise_repository.update(updated_enterprise)

        time_zone = self.time_zone_repository.get(updated_enterprise.time_zone_id)

        enterprise_dto = EnterpriseDTO.from_entity_and_timezone(
            updated_enterprise,
            time_zone,
        )

        return results.UpdateEnterpriseResult.updated(enterprise_dto)

    def delete(self, enterprise_id: EnterpriseId):
        self.enterprise_repository.delete(enterprise_id)

    def delete_by_manager(
        self, command: DeleteEnterpriseCommand
    ) -> results.DeleteEnterpriseResult:
        enterprise_id = EnterpriseId(command.enterprise_id)
        manager_id = ManagerId(command.manager_id)

        enterprise = self.enterprise_repository.get(enterprise_id)

        if not self.enterprise_manager_repository.is_assignment_exist(
            enterprise_id=enterprise_id,
            manager_id=manager_id,
        ):
            return results.DeleteEnterpriseResult.not_manager(
                f'У вас нет прав менеджера в "{enterprise.name}"(id={enterprise_id.value})'
            )

        if self._has_other_managers(
            enterprise_id=enterprise_id,
            manager_id=manager_id,
        ):
            return results.DeleteEnterpriseResult.has_other_managers(
                f'Нельзя удалить предприятие "{enterprise.name}"(id={enterprise_id.value}), '
                f"потому что по нему есть другие менеджеры"
            )

        with self.unit_of_work.transaction():
            self.enterprise_manager_repository.delete(
                enterprise_id=enterprise_id,
                manager_id=manager_id,
            )
            self.enterprise_repository.delete(enterprise_id)

        return results.DeleteEnterpriseResult.deleted()

    def _has_other_managers(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        managers = self.enterprise_manager_repository.get_enterprise_assigments(
            enterprise_id
        )

        for manager in managers:
            if manager.id != manager_id:
                return True

        return False
