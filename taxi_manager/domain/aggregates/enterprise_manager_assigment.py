from dataclasses import dataclass

from ..entities.manager import ManagerId
from ..entities.enterprise import EnterpriseId

@dataclass
class EnterpriseManagerAssigment:
    manager_id: ManagerId
    enterprise_id: EnterpriseId
