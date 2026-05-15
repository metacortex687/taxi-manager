from dataclasses import dataclass
from enum import Enum

from taxi_manager.application.enterprise.dto import EnterpriseDTO


class DeleteEnterpriseStatus(Enum):
    DELETED = "deleted"
    NOT_MANAGER = "not_manager"
    HAS_OTHER_MANAGERS = "has_other_managers"


@dataclass(frozen=True)
class DeleteEnterpriseResult:
    status: DeleteEnterpriseStatus
    message: str = ""

    @classmethod
    def deleted(cls):
        return cls(status=DeleteEnterpriseStatus.DELETED)

    @classmethod
    def not_manager(cls, message: str):
        return cls(
            status=DeleteEnterpriseStatus.NOT_MANAGER,
            message=message,
        )

    @classmethod
    def has_other_managers(cls, message: str):
        return cls(
            status=DeleteEnterpriseStatus.HAS_OTHER_MANAGERS,
            message=message,
        )


class UpdateEnterpriseStatus(Enum):
    UPDATED = "updated"
    NOT_MANAGER = "not_manager"


@dataclass(frozen=True)
class UpdateEnterpriseResult:
    status: UpdateEnterpriseStatus
    enterprise_dto: EnterpriseDTO
    message: str = ""    

    @classmethod
    def updated(cls, enterprise_dto: EnterpriseDTO):
        return cls(status=UpdateEnterpriseStatus.UPDATED, enterprise_dto=enterprise_dto)

    @classmethod
    def not_manager(cls, message: str):
        return cls(
            status=UpdateEnterpriseStatus.NOT_MANAGER,
            message=message,
        )
