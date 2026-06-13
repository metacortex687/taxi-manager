from contextlib import AbstractContextManager
from typing import Protocol


class IUnitOfWork(Protocol):
    def transaction(self) -> AbstractContextManager:
        pass

    def read_only_transaction(self) -> AbstractContextManager:
        pass
