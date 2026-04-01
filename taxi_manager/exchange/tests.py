from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .admin import TimeZoneResource, EnterpriseResource
from .models import ExchangeItem

from django.db.models import QuerySet

from django.contrib.contenttypes.models import ContentType

import tablib
from import_export import resources


from django.test import TestCase

#uv run manage.py test taxi_manager.exchange.tests.ExchangeTest --settings=taxi_manager.exchange.settings_test

class ExchangeTest(TestCase):

    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(name="enterprise1", city="city", time_zone=self.time_zone)
        
    def _clear_db(self):
        Enterprise.objects.all().delete()
        TimeZone.objects.all().delete()
        ExchangeItem.objects.all().delete()


    def test_time_zone_export_json_csv(self):
        dataset = TimeZoneResource().export()

        self.assertTrue(len(dataset) > 0)
        self.assertTrue(len(dataset.json) > 0)
        self.assertTrue(len(dataset.csv) > 1) #1-я это строка заголовок

    def test_import_export_time_zone(self):        

        self.assertEqual(1, TimeZone.objects.all().count())

        dataset = TimeZoneResource().export()
        self.assertTrue(len(dataset) > 0)

        self._clear_db()
        self.assertEqual(0, TimeZone.objects.count())
        
        TimeZoneResource().import_data(dataset)

        self.assertEqual(1, TimeZone.objects.count())



    def test_import_time_zone_uses_code_as_unique_key(self): 
        self._clear_db()
        self.assertEqual(0, TimeZone.objects.all().count())

        dataset = tablib.Dataset(['UTC', '0'], headers=['code', 'utc_offset'])
        TimeZoneResource().import_data(dataset)
        self.assertEqual(1, TimeZone.objects.all().count())

        dataset = tablib.Dataset(['UTC', '10'], headers=['code', 'utc_offset'])
        TimeZoneResource().import_data(dataset)
        self.assertEqual(1, TimeZone.objects.all().count())

        dataset = tablib.Dataset(['123', '0'], headers=['code', 'utc_offset'])
        TimeZoneResource().import_data(dataset)
        self.assertEqual(2, TimeZone.objects.all().count())


    def test_export_time_zone_does_not_include_id(self): 
        dataset = TimeZoneResource().export()
        headers = dataset.headers

        self.assertTrue(type(headers) is list)
        self.assertTrue("code" in headers)
        self.assertTrue("utc_offset" in headers)
        self.assertFalse("id" in headers)


    def test_export_enterprise_create_uuid(self):
        dataset = EnterpriseResource().export()

        self.assertTrue("exchange_uuid" in dataset.headers)
        self.assertTrue(dataset["exchange_uuid"][0] != "")


    def test_export_enterprise_create_uuid_only_once(self):
        first_dataset = EnterpriseResource().export()
        first_exchange_uuid = first_dataset ["exchange_uuid"][0]

        second_dataset = EnterpriseResource().export()
        self.assertEqual(first_exchange_uuid, second_dataset["exchange_uuid"][0])

        ExchangeItem.objects.all().delete() #После удаление уникальный идентификатор пересоздастся
        third_dataset = EnterpriseResource().export()
        self.assertNotEqual(first_exchange_uuid, third_dataset["exchange_uuid"][0])


    def test_import_enterprise(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count()) 

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()

        self._clear_db()
        self.assertEqual(0, TimeZone.objects.all().count())
        self.assertEqual(0, Enterprise.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())  

    def test_import_enterprise_creates_exchange_item(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count()) 

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()

        self._clear_db()

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

        self.assertTrue(ExchangeItem.objects.filter(uuid=dataset_enterprise["exchange_uuid"][0], content_type = ContentType.objects.get_for_model(Enterprise) ).exists())
  

    def test_import_enterprise_only_once(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count()) 

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()

        self._clear_db()
        self.assertEqual(0, TimeZone.objects.all().count())
        self.assertEqual(0, Enterprise.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())  

        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        self.assertEqual(1, Enterprise.objects.all().count()) 













        


    


        











    









        
