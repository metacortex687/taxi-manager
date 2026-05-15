from dataclasses import dataclass

from taxi_manager.domain.entities.enterprise import EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId


@dataclass(frozen=True)
class DeleteEnterpriseCommand:
    enterprise_id: int
    manager_id: int

@dataclass(frozen=True)
class UpdateEnterpriseCommand:
    manager_id: int
    enterprise_id: int
    name: str
    city: str
    time_zone_id: int 
    
