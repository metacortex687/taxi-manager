from django.test import TestCase
from taxi_manager.time_zones.models import TimeZone
from taxi_manager.enterprise.models import Enterprise

class ImportExportTest(TestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(name="enterprise1", city="city")
        
    def test_OK(self):
        pass
