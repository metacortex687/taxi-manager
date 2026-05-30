from zoneinfo import ZoneInfo


from taxi_manager.infrastructure.cache_manager.decorators import cached_method
from taxi_manager.infrastructure.vehicle.models import Vehicle, VehicleDriver
from taxi_manager.infrastructure.enterprise.models import Enterprise, Manager
from taxi_manager.raw_application.chat_bot.interfaces import (
    ICacheManager,
    IEnterpriseRepository,
    IVehicleRepository,
)


class VehicleRepository(IVehicleRepository):
    @cached_method(
        key_fn=lambda car_id: f"vehicle:time_zone:{car_id}",
    )
    def time_zone(self, car_id):  # TODO возвращать в get_by_id
        result = (
            Vehicle.objects.filter(id=car_id)
            .values_list("enterprise__time_zone__code", flat=True)
            .first()
        )
        return ZoneInfo(result)

    @cached_method(
        key_fn=lambda car_id, user_id: f"vehicle:user_have_access:{car_id}:{user_id}",
    )
    def user_have_access(self, car_id, user_id):
        return Vehicle.objects.filter(
            id=car_id,
            enterprise__manager_users__id=user_id,
        ).exists()

    @cached_method(
        key_fn=lambda number: f"vehicle:id_by_number:{number}",
    )
    def id_by_number(self, number: str):
        return (
            Vehicle.objects.filter(number=number.strip())
            .values_list("id", flat=True)
            .first()
        )

    @cached_method(
        key_fn=lambda car_id: f"vehicle:get_by_id:{car_id}",
    )
    def get_by_id(self, car_id):
        return (
            Vehicle.objects.filter(id=car_id)
            .values(
                "id",
                "number",
                "enterprise_id",
                "model__name",
                "model__id",
                "model__color",
                "model__name",
                "vin",
                "year_of_manufacture",
                "mileage",
                "price",
                "purchased_at",
            )
            .first()
        )

    @cached_method(
        key_fn=lambda car_id: f"vehicle:get_active_driver_id:{car_id}",
    )
    def get_active_driver_id(self, car_id):
        return (
            VehicleDriver.objects.filter(vehicle_id=car_id, active=True)
            .values_list("driver_id", flat=True)
            .first()
        )

    @cached_method(
        key_fn=lambda car_id: f"vehicle:get_driver_ids:{car_id}",
    )
    def get_driver_ids(self, car_id):
        return list(
            VehicleDriver.objects.filter(vehicle_id=car_id).values_list(
                "driver_id", flat=True
            )
        )


class EnterpriseRepository(IEnterpriseRepository):
    @cached_method(
        key_fn=lambda enterprise_id: f"enterprise:time_zone:{enterprise_id}",
    )
    def time_zone(self, enterprise_id):
        return ZoneInfo(
            Enterprise.objects.filter(id=enterprise_id)
            .values_list("time_zone__code", flat=True)
            .first()
        )

    @cached_method(
        key_fn=lambda user_id: f"enterprise:manager_enterprise_ids:{user_id}",
    )
    def manager_enterprise_ids(self, user_id):
        return list(
            Enterprise.objects.filter(manager_users__id=user_id).values_list(
                "id", flat=True
            )
        )

    @cached_method(
        key_fn=lambda enterprise_id: f"enterprise:assigment_manager_ids:{enterprise_id}",
    )
    def assigment_manager_ids(self, enterprise_id):
        return list(
            Enterprise.objects.filter(id=enterprise_id).values_list(
                "manager_users__id", flat=True
            )
        )

    @cached_method(
        key_fn=lambda enterprise_id: f"enterprise:vehicle_ids:{enterprise_id}",
    )
    def vehicle_ids(self, enterprise_id):
        return list(
            Enterprise.objects.filter(id=enterprise_id).values_list(
                "vehicles", flat=True
            )
        )

    @cached_method(
        key_fn=lambda enterprise_ids: f"enterprise:enterprises_info_dict:{enterprise_ids}",
    )
    def enterprises_info_dict(self, enterprise_ids):
        return {
            enterprise_id: {"name": name, "time_zone": ZoneInfo(time_zone_code)}
            for enterprise_id, name, time_zone_code in (
                Enterprise.objects.filter(id__in=enterprise_ids).values_list(
                    "id", "name", "time_zone__code"
                )
            )
        }
