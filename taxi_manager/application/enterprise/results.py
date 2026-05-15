from dataclasses import dataclass
from enum import Enum


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