from dataclasses import dataclass

@dataclass(frozen=True)
class TimeZone:
    name: str
    offset: int

@dataclass(frozen=True)
class EnterpriseId:
    value: int

@dataclass(frozen=True)
class ManagerId:
    value: int

@dataclass
class EnterpriseManagerAssignment:
    manager_id: ManagerId


@dataclass
class Enterprise:
    id: EnterpriseId
    name: str
    city: str
    time_zone: TimeZone

@dataclass
class EnterpriseManager:
    enterprise_id: EnterpriseId
    manager_id: Manager