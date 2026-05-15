from abc import ABC, abstractmethod 

from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId


class EnterpriseManagerAssigmentRepInterface(ABC):
    @abstractmethod
    def get_manager_assigments(self, manager_id:ManagerId) -> list[Enterprise]:
        pass

    @abstractmethod
    def delete(self, enterprise_id: EnterpriseId, manager_id: ManagerId):
        pass