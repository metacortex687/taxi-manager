from zoneinfo import ZoneInfo


from taxi_manager.infrastructure.vehicle.models import Vehicle
from taxi_manager.infrastructure.enterprise.models import Enterprise, Manager
from taxi_manager.raw_application.chat_bot.interfaces import IEnterpriseRepository, IVehicleRepository


class VehicleRepository(IVehicleRepository):
    def time_zone(self, car_id): #TODO возвращать в get_by_id
        result = (
            Vehicle.objects.filter(id=car_id)
            .values_list("enterprise__time_zone__code", flat=True)
            .first()
        )
        return ZoneInfo(result)

    def user_have_access(self, car_id, user_id):
        return Vehicle.objects.filter(
            id=car_id,
            enterprise__manager_users__id=user_id,
        ).exists()

    def id_by_number(self, number: str):
        return (
            Vehicle.objects.filter(number=number.strip())
            .values_list("id", flat=True)
            .first()
        )
    
    def get_by_id(self, car_id):
        return Vehicle.objects.filter(id=car_id).values("id", "number", "enterprise_id").first()


class EnterpriseRepository(IEnterpriseRepository):
    def time_zone(self, enterprise_id):
        return ZoneInfo(
            Enterprise.objects.filter(id=enterprise_id)
            .values_list("time_zone__code", flat=True)
            .first()
        )

    def manager_enterprise_ids(self, user_id):
        return list(
            Enterprise.objects.filter(manager_users__id=user_id).values_list(
                "id", flat=True
            )
        )
    
    def assigment_manager_ids(self, enterprise_id):
        return list(
            Enterprise.objects.filter(id=enterprise_id).values_list(
                "manager_users__id", flat=True
            )
        )


    def vehicle_ids(self, enterprise_id):
        return list(
            Enterprise.objects.filter(id=enterprise_id).values_list(
                "vehicles", flat=True
            )
        )

    def enterprises_info_dict(self, enterprise_ids):
        return {
            enterprise_id: {"name": name, "time_zone": ZoneInfo(time_zone_code)}
            for enterprise_id, name, time_zone_code in (
                Enterprise.objects.filter(
                    id__in=enterprise_ids
                ).values_list("id", "name", "time_zone__code")
            )
        }
