from django.test import SimpleTestCase

from taxi_manager.application.enterprise_manager_assignment.enterprise_manager_assignment_repository import (
    IEnterpriseManagerAssignmentRepository,
)
from taxi_manager.application.time_zone.time_zone_repository import (
    ITimeZoneRepository,
)
from taxi_manager.application.enterprise_manager_assignment.enterprise_manager_usecase import (
    EnterpriseManagerUseCase,
)
from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.domain.entities.time_zone import TimeZone, TimeZoneId


class FakeEnterpriseManagerRepository(IEnterpriseManagerAssignmentRepository):
    def get_manager_assigments(self, manager_id: ManagerId) -> list[Enterprise]:
        return [
            Enterprise(
                id=EnterpriseId(1),
                name="Enterprise 1",
                city="Almaty",
                time_zone_id=TimeZoneId(1),
            )
        ]


class FakeTimeZoneRepository(ITimeZoneRepository):
    def get_list(self, time_zone_ids: list[TimeZoneId]) -> list[TimeZone]:
        return [
            TimeZone(id=TimeZoneId(1), code="Asia/Almaty", utc_offset=5),
            TimeZone(id=TimeZoneId(2), code="test2", utc_offset=0),
        ]

    def get(self, time_zone_id):
        raise NotImplementedError


class EnterpriseManagerUseCaseTest(SimpleTestCase):
    def test_get_manager_assigments_returns_enterprise_dto_list(self):
        usecase = EnterpriseManagerUseCase(
            enterprise_manager_assigment_rep=FakeEnterpriseManagerRepository(),
            time_zone_rep=FakeTimeZoneRepository(),
        )

        result = usecase.get_manager_assigments(ManagerId(1))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].name, "Enterprise 1")
        self.assertEqual(result[0].city, "Almaty")
        self.assertEqual(result[0].time_zone, 1)
        self.assertEqual(result[0].time_zone_code, "Asia/Almaty")
