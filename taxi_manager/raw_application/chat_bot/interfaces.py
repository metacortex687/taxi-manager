from typing import Generator, Iterator


class IChatBotClient:

    def listen(self) -> Iterator[tuple[str, str]]:  # (text, user_id)
        raise NotImplementedError

    def send(self, user_id: str, message: str):
        raise NotImplementedError

class IChatReportService:
    def list_reports(self) -> list[str]:
        raise NotImplementedError
    
    def report(command_line: str) -> list[str]:
        raise NotImplementedError        

class IEnterpriseRepository:
    def time_zone(self, enterprise_id):
        raise NotImplementedError

    def manager_enterprise_ids(self, user_id):
        raise NotImplementedError
    
    def assigment_manager_ids(self, enterprise_id):
        raise NotImplementedError


    def vehicle_ids(self, enterprise_id):
        raise NotImplementedError

    def enterprises_info_dict(self, enterprise_ids):
        raise NotImplementedError

class IVehicleRepository:
    def time_zone(self, car_id): #TODO возвращать в get_by_id
        raise NotImplementedError
    
    def user_have_access(self, car_id, user_id):
        raise NotImplementedError

    def id_by_number(self, number: str):
        raise NotImplementedError
    
    def get_by_id(self, car_id):
        raise NotImplementedError
    
    def get_active_driver_id(self, car_id):
        raise NotImplementedError

    
    def get_driver_ids(self, car_id):
        raise NotImplementedError
