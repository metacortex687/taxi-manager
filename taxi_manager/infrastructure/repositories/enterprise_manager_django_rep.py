from taxi_manager.application.enterprise_manager_assignment.repository import (
    IEnterpriseManagerAssignmentRepository,
)

from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.time_zone import TimeZoneId

from taxi_manager.domain.entities.manager import Manager, ManagerId

from taxi_manager.infrastructure.enterprise.models import Manager as ManagerOrm


class EnterpriseManagerDjangoRep(IEnterpriseManagerAssignmentRepository):
    def get_manager_assigments(self, manager_id: ManagerId) -> list[Enterprise]:
        orm_objects = ManagerOrm.objects.filter(user=manager_id.value).values(
            "user_id",
            "enterprise_id",
            "enterprise__name",
            "enterprise__city",
            "enterprise__time_zone_id",
        )
        return [
            Enterprise(
                id=EnterpriseId(obj["enterprise_id"]),
                name=obj["enterprise__name"],
                city=obj["enterprise__city"],
                time_zone_id=TimeZoneId(obj["enterprise__time_zone_id"]),
            )
            for obj in orm_objects
        ]

    def get_enterprise_assigments(
        self, enterprise_id: EnterpriseId
    ) -> list[Manager]:
        orm_objects = ManagerOrm.objects.filter(enterprise=enterprise_id.value).values(
            "user_id",
            "enterprise_id",
            "enterprise__name",
            "enterprise__city",
            "enterprise__time_zone_id",
        )
        return [
            Manager(
                id=ManagerId(obj["user_id"]),
            )
            for obj in orm_objects
        ]

    def is_assignment_exist(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        return ManagerOrm.objects.filter(
            user=manager_id.value, enterprise=enterprise_id.value
        ).exists()

    def delete(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        ManagerOrm.objects.filter(
            user=manager_id.value, enterprise=enterprise_id.value
        ).delete()

    def create(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        ManagerOrm.objects.get_or_create(
            user_id=manager_id.value,
            enterprise_id=enterprise_id.value,
        )