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

    def get_queryset_a(self, model_class) -> QuerySet:
        return model_class._default_manager.using("default")
    
    def get_queryset_b(self, model_class) -> QuerySet:
        return model_class._default_manager.using("import_target") 

    def get_resource_a(self, resource_class) -> resources.ModelResource:
        return resource_class(db_alias="default")
    
    def get_resource_b(self, resource_class) -> resources.ModelResource:
        return resource_class(db_alias="import_target")


    def setUp(self):
        self.time_zone = self.get_queryset_a(TimeZone).create(code="UTC", utc_offset=0)
        self.enterprise1 = self.get_queryset_a(Enterprise).create(name="enterprise1", city="city", time_zone=self.time_zone)
        

    def test_time_zone_export_json_csv(self):
        dataset = self.get_resource_a(TimeZoneResource).export()

        self.assertTrue(len(dataset) > 0)
        self.assertTrue(len(dataset.json) > 0)
        self.assertTrue(len(dataset.csv) > 1) #1-я это строка заголовок


    def test_can_use_two_databases(self):
        self.assertEqual(1, self.get_queryset_a(Enterprise).count())
        self.assertEqual(0, self.get_queryset_b(Enterprise).count())
        

    def test_import_export_time_zone(self):        

        self.assertEqual(1, self.get_queryset_a(TimeZone).count())
        self.assertEqual(0, self.get_queryset_b(TimeZone).count())

        dataset = self.get_resource_a(TimeZoneResource).export()
        self.assertTrue(len(dataset) > 0)

        self.get_resource_b(TimeZoneResource).import_data(dataset)

        self.assertEqual(1, self.get_queryset_a(TimeZone).count())
        self.assertEqual(1, self.get_queryset_b(TimeZone).count())











    









        
