from django.test import TestCase

from django.contrib.auth import get_user_model

from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.infrastructure.enterprise.models import Enterprise
from taxi_manager.infrastructure.time_zones.models import TimeZone

from .enterprise_manager_django_rep import EnterpriseManagerDjangoRep


class EnterpriseManagerRepositoryTest(TestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(
            name="enterprise1", city="city", time_zone=self.time_zone
        )
        self.enterprise2 = Enterprise.objects.create(
            name="enterprise2", city="city", time_zone=self.time_zone
        )
        self.enterprise3 = Enterprise.objects.create(
            name="enterprise3", city="city", time_zone=self.time_zone
        )

        self.manager1 = get_user_model().objects.create_user(
            username="manager1", email="manager1@mail.com", password="secret"
        )
        self.manager2 = get_user_model().objects.create_user(
            username="manager2", email="manager1@mail.com", password="secret"
        )

        self.manager1.managed_enterprises.add(self.enterprise1)
        self.manager1.managed_enterprises.add(self.enterprise2)

        self.manager2.managed_enterprises.add(self.enterprise2)
        self.manager2.managed_enterprises.add(self.enterprise3)

    def test_get_manager_enterprises(self):
        rep = EnterpriseManagerDjangoRep()
        result = rep.get_manager_assigments(ManagerId(self.manager1.id))
        print(result)
