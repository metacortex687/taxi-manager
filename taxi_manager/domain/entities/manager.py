from dataclasses import dataclass

@dataclass(frozen=True)
class ManagerId:
    value: int

@dataclass
class Manager:
    id: ManagerId