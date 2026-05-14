from django.test import TestCase

from django.contrib.auth import get_user_model


from taxi_manager.domain.entities.time_zone import TimeZoneId
from taxi_manager.infrastructure.repositories.time_zone_django_rep import (
    TimeZoneDjangoRep,
)
from taxi_manager.infrastructure.time_zones.models import TimeZone as TimeZoneOrm

from .enterprise_manager_django_rep import EnterpriseManagerDjangoRep


class EnterpriseManagerRepositoryTest(TestCase):
    def setUp(self):
        self.time_zone1 = TimeZoneOrm.objects.create(code="tz 1", utc_offset=1)
        self.time_zone2 = TimeZoneOrm.objects.create(code="tz 2", utc_offset=2)
        self.time_zone3 = TimeZoneOrm.objects.create(code="tz 3", utc_offset=3)
        self.time_zone4 = TimeZoneOrm.objects.create(code="tz 4", utc_offset=4)

    def test_get_list(self):
        rep = TimeZoneDjangoRep()
        result = rep.get_list(
            [TimeZoneId(self.time_zone2.id), TimeZoneId(self.time_zone4.id)]
        )

        print(result)
