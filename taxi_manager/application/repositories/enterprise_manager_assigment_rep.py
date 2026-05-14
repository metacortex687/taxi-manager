from abc import ABC, abstractmethod 

from taxi_manager.domain.entities.enterprise import Enterprise
from taxi_manager.domain.entities.manager import ManagerId


class EnterpriseManagerAssigmentRepInterface(ABC):
    @abstractmethod
    def get_manager_assigments(self, manager_id:ManagerId) -> list[Enterprise]:
        pass