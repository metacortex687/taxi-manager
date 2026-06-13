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


    def create_model_in_serializable_thread(self, start, done, errors: list):
        uow = DjangoUnitOfWork()
        try:
            with uow.serializable_transaction():
                if not start.wait(timeout=5):
                    raise TimeoutError("Поток не получил сигнал start")
                
                self.assertEqual(Model.objects.count(), 1) #без этого не будет ошибки

                self._create_model("new")
        except BaseException as exc:
            errors.append(exc)
        finally:
            connections.close_all()
            done.set()

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


    def test_serializable_transaction_provide_consistent_snapshot(self):
        uow = DjangoUnitOfWork()
        start = threading.Event()
        done = threading.Event()

        thread = threading.Thread(
            target=self.create_model_in_thread, args=(start, done, [])
        )
        thread.start()

        with uow.serializable_transaction():
            self.assertEqual(Model.objects.count(), 1)

            start.set()
            done.wait()

            self.assertEqual(Model.objects.count(), 1)

        thread.join()

        self.assertEqual(Model.objects.count(), 2)

    def test_read_only_transaction_does_not_allow_writes(self):
        uow = DjangoUnitOfWork()

        with self.assertRaises(DatabaseError):
            with uow.read_only_transaction():
                self._create_model("new")

        self.assertEqual(Model.objects.count(), 1)

    def test_serializable_transaction_allows_writes(self):
        uow = DjangoUnitOfWork()

        with uow.serializable_transaction():
            self._create_model("new")

        self.assertEqual(Model.objects.count(), 2)

    def test_read_only_transaction_allows_parallel_writes(self):
        uow = DjangoUnitOfWork()
        start = threading.Event()
        done = threading.Event()
        errors = []

        thread = threading.Thread(
            target=self.create_model_in_thread,
            args=(start, done, errors),
        )
        thread.start()

        with uow.read_only_transaction():
            self.assertEqual(Model.objects.count(), 1)

            start.set()
            self.assertTrue(done.wait())

            self.assertEqual(errors, [])
            self.assertEqual(Model.objects.count(), 1)

        thread.join()

        self.assertEqual(Model.objects.count(), 2)


    def test_serializable_transaction_raises_error_on_conflicting_parallel_write(self):
        uow = DjangoUnitOfWork()
        start = threading.Event()
        done = threading.Event()
        errors = []

        thread = threading.Thread(
            target=self.create_model_in_serializable_thread,
            args=(start, done, errors),
        )
        thread.start()

        with self.assertRaisesRegex(
            OperationalError,
            "could not serialize access due to read/write dependencies among transactions",
        ):
            with uow.serializable_transaction():
                self.assertEqual(Model.objects.count(), 1)

                start.set()
                self.assertTrue(done.wait())

                self.assertEqual(Model.objects.count(), 1) #используется снимок на начало транзакции

                self._create_model("new-main2")       
            

        thread.join()

        self.assertEqual(Model.objects.count(), 2) #одна из транзакций была принята