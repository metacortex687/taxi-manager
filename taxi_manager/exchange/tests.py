from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone
from taxi_manager.vehicle.models import Vehicle, Model

from .resources import VehicleResource, EnterpriseResource, TimeZoneResource, ModelResource
from .models import ExchangeItem

from django.db.models import QuerySet

from django.contrib.contenttypes.models import ContentType


from import_export import resources
import tablib

from django.test import TestCase


# uv run manage.py test taxi_manager.exchange.tests


def dataset_from_dict(data: dict) -> tuple[list, list]:
    return tablib.Dataset(list(data.values()), headers=list(data.keys()))


def clear_db():
    ExchangeItem.objects.all().delete()

    Vehicle.objects.all().delete()
    Enterprise.objects.all().delete()
    TimeZone.objects.all().delete()

    Model.objects.all().delete()



class ExchangeTimeZoneTest(TestCase):
    def setUp(self):
        self.time_zone = {
            "code": "UTC",
            "utc_offset": 0,
        }
        
        TimeZone.objects.create(**self.time_zone)

    def test_time_zone_export_json_csv(self):
        dataset = TimeZoneResource().export()

        self.assertTrue(len(dataset) > 0)
        self.assertTrue(len(dataset.json) > 0)
        self.assertTrue(len(dataset.csv) > 1)  # 1-я это строка заголовок

    def test_import_export_time_zone(self):
        self.assertEqual(1, TimeZone.objects.all().count())

        dataset = TimeZoneResource().export()
        self.assertTrue(len(dataset) > 0)

        clear_db()
        self.assertEqual(0, TimeZone.objects.count())

        TimeZoneResource().import_data(dataset)

        self.assertEqual(1, TimeZone.objects.count())

    def test_import_time_zone_uses_code_as_unique_key(self):
        clear_db()
        self.assertEqual(0, TimeZone.objects.all().count())

        dataset = tablib.Dataset(["UTC", "0"], headers=["code", "utc_offset"])
        TimeZoneResource().import_data(dataset)
        self.assertEqual(1, TimeZone.objects.all().count())

        dataset = tablib.Dataset(["UTC", "10"], headers=["code", "utc_offset"])
        TimeZoneResource().import_data(dataset)
        self.assertEqual(1, TimeZone.objects.all().count())

        dataset = tablib.Dataset(["123", "0"], headers=["code", "utc_offset"])
        TimeZoneResource().import_data(dataset)
        self.assertEqual(2, TimeZone.objects.all().count())

    def test_export_time_zone_does_not_include_id(self):
        dataset = TimeZoneResource().export()
        headers = dataset.headers

        self.assertTrue(type(headers) is list)
        self.assertTrue("code" in headers)
        self.assertTrue("utc_offset" in headers)
        self.assertFalse("id" in headers)


class ExchangeModelTest(TestCase):
    def setUp(self):
        self._class_resource = ModelResource
        self._class_model = Model

        self.model1 = {
            "name": "model1",
            "type": "PCR",
            "number_of_seats": 5,
            "tank_capacity_l": 20,
            "load_capacity_kg": 500,
        }
        Model.objects.create(**self.model1)


    def test_model_export_json_csv(self):
        dataset = ModelResource().export()

        self.assertTrue(len(dataset) > 0)
        self.assertTrue(len(dataset.json) > 0)
        self.assertTrue(len(dataset.csv) > 1)  # 1-я это строка заголовок

    def test_import_export_model(self):
        self.assertEqual(1, Model.objects.all().count())

        dataset = ModelResource().export()
        self.assertTrue(len(dataset) > 0)

        clear_db()
        self.assertEqual(0, Model.objects.count())

        ModelResource().import_data(dataset, raise_errors=True)

        self.assertEqual(1, Model.objects.count())

    def test_import_model_uses_name_as_unique_key(self):
        clear_db()
        self.assertEqual(0, Model.objects.all().count())

        ModelResource().import_data(dataset_from_dict(self.model1))
        self.assertEqual(1, Model.objects.all().count())

        self.model1["number_of_seats"] = 10
        ModelResource().import_data(dataset_from_dict(self.model1))
        self.assertEqual(1, Model.objects.all().count())

        self.model1["name"] = "new_name"
        ModelResource().import_data(dataset_from_dict(self.model1))
        self.assertEqual(2, Model.objects.all().count())

    def test_export_model_does_not_include_id(self):
        dataset = ModelResource().export()
        headers = dataset.headers

        self.assertTrue(type(headers) is list)
        self.assertTrue("name" in headers)
        self.assertTrue("type" in headers)
        self.assertTrue("number_of_seats" in headers)
        self.assertTrue("tank_capacity_l" in headers)
        self.assertTrue("load_capacity_kg" in headers)
        self.assertFalse("id" in headers)


class ExchangeEnterpriseTest(TestCase):
    def setUp(self):
        self.time_zone = {
            "code": "UTC",
            "utc_offset": 0,
        }

        time_zone = TimeZone.objects.create(**self.time_zone)

        self.enterprise1 = {
            "name": "enterprise1",
            "city": "city",
            "time_zone": time_zone,
        }

        Enterprise.objects.create(**self.enterprise1)

    def _clear_db(self):
        ExchangeItem.objects.all().delete()

        Enterprise.objects.all().delete()
        TimeZone.objects.all().delete()

    def test_export_enterprise_create_uuid(self):
        dataset = EnterpriseResource().export()

        self.assertTrue("exchange_uuid" in dataset.headers)
        self.assertTrue(dataset["exchange_uuid"][0] != "")

    def test_export_enterprise_create_uuid_only_once(self):
        first_dataset = EnterpriseResource().export()
        first_exchange_uuid = first_dataset["exchange_uuid"][0]

        second_dataset = EnterpriseResource().export()
        self.assertEqual(first_exchange_uuid, second_dataset["exchange_uuid"][0])

        ExchangeItem.objects.all().delete()  # После удаление уникальный идентификатор пересоздастся
        third_dataset = EnterpriseResource().export()
        self.assertNotEqual(first_exchange_uuid, third_dataset["exchange_uuid"][0])

    def test_import_enterprise(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()

        clear_db()
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

        clear_db()

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

        self.assertTrue(
            ExchangeItem.objects.filter(
                uuid=dataset_enterprise["exchange_uuid"][0],
                content_type=ContentType.objects.get_for_model(Enterprise),
            ).exists()
        )

    def test_import_enterprise_only_once(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()

        clear_db()
        self.assertEqual(0, TimeZone.objects.all().count())
        self.assertEqual(0, Enterprise.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        self.assertEqual(1, Enterprise.objects.all().count())

    def test_import_enterprise_updates_existing_object(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()

        clear_db()
        self.assertEqual(0, TimeZone.objects.all().count())
        self.assertEqual(0, Enterprise.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        self.assertEqual(Enterprise.objects.first().name, "enterprise1")

        exchange_uuid, name, city, time_zone  = dataset_enterprise[0]
        dataset_enterprise[0] = (exchange_uuid, "new_name", city, time_zone)

        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        self.assertEqual(1, Enterprise.objects.all().count())
        self.assertEqual(Enterprise.objects.first().name, "new_name")



class ExchangeVehicleTest(TestCase):
    def setUp(self):
        self.time_zone = {
            "code": "UTC",
            "utc_offset": 0,
        }

        time_zone = TimeZone.objects.create(**self.time_zone)

        self.enterprise1 = {
            "name": "enterprise1",
            "city": "city",
            "time_zone": time_zone,
        }

        enterprise1 = Enterprise.objects.create(**self.enterprise1)

        self.model1 = {
            "name": "model1",
            "type": "PCR",
            "number_of_seats": 5,
            "tank_capacity_l": 20,
            "load_capacity_kg": 500,
        }

        model1 = Model.objects.create(**self.model1)

        self.vehicle1 = {
            "model": model1,
            "number": "num1",
            "vin": "Z948741AA12323456",
            "year_of_manufacture": 2025,
            "mileage": 100,
            "enterprise": enterprise1,
            "price": 125000,
        }

        Vehicle.objects.create(**self.vehicle1)

    def test_export_vehicle_create_uuid(self):
        EnterpriseResource().export()
        dataset = VehicleResource().export()

        self.assertTrue("exchange_uuid" in dataset.headers)
        self.assertTrue(dataset["exchange_uuid"][0] != "")

    def test_export_vehicle_create_uuid_only_once(self):
        EnterpriseResource().export()
        first_dataset = VehicleResource().export()
        first_exchange_uuid = first_dataset["exchange_uuid"][0]

        second_dataset = VehicleResource().export()
        self.assertEqual(first_exchange_uuid, second_dataset["exchange_uuid"][0])

        ExchangeItem.objects.filter(content_type = ExchangeItem.get_content_type_for_model(Vehicle)).delete()  # После удаление уникальный идентификатор пересоздастся
        third_dataset = VehicleResource().export()
        self.assertNotEqual(first_exchange_uuid, third_dataset["exchange_uuid"][0])

    def test_vehicle_export_uses_enterprise_exchange_uuid_for_foreign_key(self):
        dataset_enterprise = EnterpriseResource().export()
        dataset_vehicle = VehicleResource().export()

        self.assertEqual(dataset_vehicle["enterprise"][0], dataset_enterprise["exchange_uuid"][0])

    def test_vehicle_export_raises_error_if_enterprise_exchange_uuid_is_missing(self):
        with self.assertRaisesMessage(
            ValueError,
            "Невозможно выполнить экспорт значения "
        ):
            VehicleResource().export()



    # def test_import_vehicle(self):
    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    #     dataset_time_zone = TimeZoneResource().export()
    #     dataset_enterprise = EnterpriseResource().export()

    #     clear_db()
    #     self.assertEqual(0, TimeZone.objects.all().count())
    #     self.assertEqual(0, Enterprise.objects.all().count())

    #     TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
    #     EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    # def test_import_enterprise_creates_exchange_item(self):
    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    #     dataset_time_zone = TimeZoneResource().export()
    #     dataset_enterprise = EnterpriseResource().export()

    #     clear_db()

    #     TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
    #     EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

    #     self.assertTrue(
    #         ExchangeItem.objects.filter(
    #             uuid=dataset_enterprise["exchange_uuid"][0],
    #             content_type=ContentType.objects.get_for_model(Enterprise),
    #         ).exists()
    #     )

    # def test_import_enterprise_only_once(self):
    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    #     dataset_time_zone = TimeZoneResource().export()
    #     dataset_enterprise = EnterpriseResource().export()

    #     clear_db()
    #     self.assertEqual(0, TimeZone.objects.all().count())
    #     self.assertEqual(0, Enterprise.objects.all().count())

    #     TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
    #     EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    #     EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
    #     self.assertEqual(1, Enterprise.objects.all().count())

    # def test_import_enterprise_updates_existing_object(self):
    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    #     dataset_time_zone = TimeZoneResource().export()
    #     dataset_enterprise = EnterpriseResource().export()

    #     clear_db()
    #     self.assertEqual(0, TimeZone.objects.all().count())
    #     self.assertEqual(0, Enterprise.objects.all().count())

    #     TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
    #     EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)

    #     self.assertEqual(1, TimeZone.objects.all().count())
    #     self.assertEqual(1, Enterprise.objects.all().count())

    #     self.assertEqual(Enterprise.objects.first().name, "enterprise1")

    #     name, city, time_zone, exchange_uuid = dataset_enterprise[0]
    #     dataset_enterprise[0] = ("new_name", city, time_zone, exchange_uuid)

    #     EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
    #     self.assertEqual(1, Enterprise.objects.all().count())
    #     self.assertEqual(Enterprise.objects.first().name, "new_name")