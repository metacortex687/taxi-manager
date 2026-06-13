import threading

from django.db import DatabaseError, OperationalError, connections
from django.test import TransactionTestCase

from taxi_manager.infrastructure.repositories.unit_of_work import DjangoUnitOfWork
from taxi_manager.infrastructure.vehicle.models import Model

#uv run manage.py test taxi_manager.infrastructure.repositories.tests_unit_of_work

class UnitOfWorkTests(TransactionTestCase):
    def setUp(self):
        self._create_model("base")

    def _create_model(self, name, errors=[]):
        Model.objects.create(
            name=name,
            type="PCR",
            number_of_seats=6,
            tank_capacity_l=50,
            load_capacity_kg=500,
        )


    def create_model_in_thread(self, start, done, errors: list):
        try:
            if not start.wait(timeout=5):
                raise TimeoutError("Поток не получил сигнал start")
            start.wait()
            self._create_model("new")
        except BaseException as exc:
            errors.append(exc)
        finally:
            connections.close_all()
            done.set()

    def test_transaction_does_not_provide_consistent_snapshot(self):
        uow = DjangoUnitOfWork()
        start = threading.Event()
        done = threading.Event()

        thread = threading.Thread(
            target=self.create_model_in_thread, args=(start, done, [])
        )
        thread.start()

        with uow.transaction():
            self.assertEqual(Model.objects.count(), 1)

            start.set()
            done.wait()

            self.assertEqual(Model.objects.count(), 2)

        thread.join()


    def test_read_only_transaction_provide_consistent_snapshot(self):
        uow = DjangoUnitOfWork()
        start = threading.Event()
        done = threading.Event()

        thread = threading.Thread(
            target=self.create_model_in_thread, args=(start, done, [])
        )
        thread.start()

        with uow.read_only_transaction():
            self.assertEqual(Model.objects.count(), 1)

            start.set()
            done.wait()

            self.assertEqual(Model.objects.count(), 1)

        thread.join()

