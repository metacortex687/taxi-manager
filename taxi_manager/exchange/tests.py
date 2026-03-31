from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .admin import TimeZoneResource

import tablib
from import_export import resources

from django.test import TestCase


class ExchangeTest(TestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(name="enterprise1", city="city")
        
    def test_time_zone_export(self):
        dataset = TimeZoneResource().export()

        self.assertTrue(len(dataset) > 0)
        self.assertTrue(len(dataset.json) > 0)
        self.assertTrue(len(dataset.csv) > 1) #1-я это строка заголовок






        
