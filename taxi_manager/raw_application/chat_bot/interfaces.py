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
