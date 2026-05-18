from abc import ABC, abstractmethod

from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.manager import Manager, ManagerId


class IEnterpriseManagerAssignmentRepository(ABC):
    @abstractmethod
    def get_manager_assigments(self, manager_id: ManagerId) -> list[Enterprise]:
        pass

    @abstractmethod
    def get_enterprise_assigments(enterprise_id: EnterpriseId) -> list[Manager]:
        pass

    @abstractmethod
    def delete(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        pass

    @abstractmethod    
    def is_assignment_exist(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        pass

    def create(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        pass