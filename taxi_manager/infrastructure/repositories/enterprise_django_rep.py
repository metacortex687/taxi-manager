from taxi_manager.application.enterprise.repository import IEnterpriseRepository
from taxi_manager.domain.entities.enterprise import EnterpriseId, Enterprise
from taxi_manager.domain.entities.time_zone import TimeZoneId
from taxi_manager.infrastructure.enterprise.models import Enterprise as EnterpriseORM


class EnterpriseDjangoRep(IEnterpriseRepository):
    def get(self, enterprise_id: EnterpriseId):
        obj = EnterpriseORM.objects.get(pk=enterprise_id.value)
        return Enterprise(
            id=EnterpriseId(obj.id),
            name=obj.name,
            city=obj.city,
            time_zone_id=TimeZoneId(obj.time_zone.id),
        )

    def update(self, enterprise: Enterprise):
        EnterpriseORM.objects.filter(id=enterprise.id.value).update(
            name=enterprise.name,
            city=enterprise.city,
            time_zone=enterprise.time_zone_id.value,
        )

    def delete(self, enterprise_id: EnterpriseId):
        EnterpriseORM.objects.filter(id=enterprise_id.value).delete()
