from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .admin import TimeZoneResource

from django.db.models import QuerySet

import tablib
from import_export import resources

from django.test import TestCase

#uv run manage.py test taxi_manager.exchange.tests.ExchangeTest --settings=taxi_manager.exchange.settings_test

class ExchangeTest(TestCase):
    databases = {"default", "import_target"}

    def get_queryset_a(self, model) -> QuerySet:
        return model._default_manager.using("default")
    
    def get_queryset_b(self, model) -> QuerySet:
        return model._default_manager.using("import_target") 


    def setUp(self):
        self.time_zone = self.get_queryset_a(TimeZone).create(code="UTC", utc_offset=0)
        self.enterprise1 = self.get_queryset_a(Enterprise).create(name="enterprise1", city="city", time_zone=self.time_zone)
        
        
    def test_time_zone_export_json_csv(self):
        dataset = TimeZoneResource().export(self.get_queryset_a(TimeZone).all())

        self.assertTrue(len(dataset) > 0)
        self.assertTrue(len(dataset.json) > 0)
        self.assertTrue(len(dataset.csv) > 1) #1-я это строка заголовок

    def test_can_use_two_databases(self):
        self.assertEqual(1, self.get_queryset_a(Enterprise).count())
        self.assertEqual(0, self.get_queryset_b(Enterprise).count())





    









        
