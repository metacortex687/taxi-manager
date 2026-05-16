from contextlib import AbstractContextManager
from typing import Protocol


class IUnitOfWork(Protocol):
    def transaction(self) -> AbstractContextManager:
        pass