from dataclasses import dataclass

from taxi_manager.domain.entities.enterprise import EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId


@dataclass(frozen=True)
class DeleteEnterpriseCommand:
    enterprise_id: int
    manager_id: int

