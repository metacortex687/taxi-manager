from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .admin import TimeZoneResource, EnterpriseResource
from .models import ExchangeItem

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


    def test_import_time_zone_uses_code_as_unique_key(self): 
        self.assertEqual(0, self.get_queryset_b(TimeZone).count())

        dataset = tablib.Dataset(['UTC', '0'], headers=['code', 'utc_offset'])
        self.get_resource_b(TimeZoneResource).import_data(dataset)
        self.assertEqual(1, self.get_queryset_b(TimeZone).count())


        dataset = tablib.Dataset(['UTC', '0'], headers=['code', 'utc_offset'])
        self.get_resource_b(TimeZoneResource).import_data(dataset)
        self.assertEqual(1, self.get_queryset_b(TimeZone).count())

        dataset = tablib.Dataset(['123', '0'], headers=['code', 'utc_offset'])
        self.get_resource_b(TimeZoneResource).import_data(dataset)
        self.assertEqual(2, self.get_queryset_b(TimeZone).count())


    def test_export_time_zone_does_not_include_id(self): 
        dataset = self.get_resource_a(TimeZoneResource).export()
        headers = dataset.headers

        self.assertTrue(type(headers) is list)
        self.assertTrue("code" in headers)
        self.assertTrue("utc_offset" in headers)
        self.assertFalse("id" in headers)


    def test_export_enterprise_create_uuid(self):
        dataset = self.get_resource_a(EnterpriseResource).export()

        self.assertTrue("exchange_uuid" in dataset.headers)
        self.assertTrue(dataset["exchange_uuid"][0] != "")


    def test_export_enterprise_create_uuid_only_once(self):
        first_dataset = self.get_resource_a(EnterpriseResource).export()
        first_exchange_uuid = first_dataset ["exchange_uuid"][0]

        second_dataset = self.get_resource_a(EnterpriseResource).export()
        self.assertEqual(first_exchange_uuid, second_dataset["exchange_uuid"][0])

        ExchangeItem.objects.all().delete() #После удаление уникальный идентификатор пересоздастся
        third_dataset = self.get_resource_a(EnterpriseResource).export()
        self.assertNotEqual(first_exchange_uuid, third_dataset["exchange_uuid"][0])








        


    


        











    









        
