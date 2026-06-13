from contextlib import contextmanager
from django.db import transaction, connection

from taxi_manager.application.unit_of_work import IUnitOfWork


class DjangoUnitOfWork(IUnitOfWork):
    def transaction(self):
        return transaction.atomic()

    @contextmanager
    def read_only_transaction(self):
         # согласованное чтение, не блокирует базу данных
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
                )

            yield


    @contextmanager
    def serializable_transaction(self):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE READ WRITE"
                )

            yield 