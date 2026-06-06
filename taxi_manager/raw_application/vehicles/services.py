from taxi_manager.application.enterprise_manager_assignment.repository import IEnterpriseManagerAssignmentRepository
from taxi_manager.domain.entities.enterprise import EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.raw_application.chat_bot.interfaces import IVehicleRepository
from taxi_manager.raw_application.dto.result import Result


class VehicleService:
    def __init__(self, vehicle_repository:IVehicleRepository, enterprise_manager_assigment_repository:IEnterpriseManagerAssignmentRepository):
        self.vehicle_repository = vehicle_repository
        self.enterprise_manager_assigment_repository = enterprise_manager_assigment_repository

    def get_by_manager(self, vehicle_id, manager_id) -> Result:

        vehicle_dict = self.vehicle_repository.get_by_id(vehicle_id)

        if not self.is_assignment_exist(vehicle_dict["enterprise_id"], manager_id): 
            return Result.not_manager(f'У вас нет прав менеджера для авто "{vehicle_dict["model__name"]} {vehicle_dict["number"]}"(id={vehicle_id})')        

        active_driver_id = self.vehicle_repository.get_active_driver_id(vehicle_id)
        driver_ids = self.vehicle_repository.get_driver_ids(vehicle_id)
        display_name = f"{vehicle_dict["model__name"]} {vehicle_dict["number"]}"

        data = {
            "id": vehicle_dict["id"],
            "display_name": display_name,
            "model_id": vehicle_dict["model__id"],
            "color": vehicle_dict["model__color"],
            "number": vehicle_dict["number"],
            "vin": vehicle_dict["vin"],
            "year_of_manufacture": vehicle_dict["year_of_manufacture"],
            "mileage": vehicle_dict["mileage"],
            "price": vehicle_dict["price"],
            "active_driver_id": active_driver_id,
            "model__name": vehicle_dict["model__name"],
            "enterprise_id": vehicle_dict["enterprise_id"],
            "purchased_at": vehicle_dict["purchased_at"],
            "driver_ids": driver_ids,
        }

        return Result.received(data)
    
    def is_assignment_exist(self, enterprise_id, manager_id):
        return self.enterprise_manager_assigment_repository.is_assignment_exist(EnterpriseId(enterprise_id), ManagerId(manager_id))