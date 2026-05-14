from taxi_manager.application.repositories.enterprise_rep import EnterpriseRepInterface
from taxi_manager.domain.entities.enterprise import EnterpriseId, Enterprise
from taxi_manager.domain.entities.time_zone import TimeZoneId
from taxi_manager.infrastructure.enterprise.models import Enterprise as EnterpriseORM


class EnterpriseDjangoRep(EnterpriseRepInterface):
    def get(self, enterprise_id: EnterpriseId):
        obj = EnterpriseORM.objects.get(pk=enterprise_id.value)
        return Enterprise(
            id=EnterpriseId(obj.id),
            name=obj.name,
            city=obj.city,
            time_zone_id=TimeZoneId(obj.time_zone.id),
        )
