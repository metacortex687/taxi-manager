from abc import ABC, abstractmethod 

from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId



class EnterpriseRepInterface(ABC):
    @abstractmethod
    def get(self, enterprise_id:EnterpriseId) -> Enterprise:
        pass

    @abstractmethod
    def update(self, enterprise: Enterprise):
        pass