from zoneinfo import ZoneInfo

from taxi_manager.infrastructure.vehicle.models import Vehicle


class VehicleRepository:
    def time_zone(self, car_id):
        result = (
                Vehicle.objects.filter(id=car_id)
                .values_list("enterprise__time_zone__code", flat=True)
                .first()
            )     
        return ZoneInfo(result)
    
    def user_have_access(self, car_id, user_id):
        return (
            Vehicle.objects
            .filter(
                id=car_id,
                enterprise__manager_users__id=user_id,
            )
            .exists()
        )    

