from taxi_manager.application.repositories.enterprise_manager_assigment_rep import (
    EnterpriseManagerAssigmentRepInterface,
)

from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.time_zone import TimeZoneId

from taxi_manager.domain.entities.manager import ManagerId

from taxi_manager.infrastructure.enterprise.models import Manager as ManagerOrm


class EnterpriseManagerDjangoRep(EnterpriseManagerAssigmentRepInterface):
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
                time_zone=TimeZoneId(obj["enterprise__time_zone_id"]),
            )
            for obj in orm_objects
        ]
