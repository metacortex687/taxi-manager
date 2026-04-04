from taxi_manager.geo_tracking.models import VehicleLocation
from taxi_manager.vehicle.models import Vehicle, Model
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.time_zones.models import TimeZone

from .resources import VehicleLocationResource, VehicleResource, EnterpriseResource, TimeZoneResource, ModelResource
from .models import ExchangeItem

from django.db.models import QuerySet

from django.contrib.contenttypes.models import ContentType

from django.contrib.gis.geos import Point

from datetime import datetime, UTC

from import_export import resources, exceptions
import tablib

from django.test import TestCase


# uv run manage.py test taxi_manager.exchange.tests


def dataset_from_dict(data: dict) -> tuple[list, list]:
    return tablib.Dataset(list(data.values()), headers=list(data.keys()))


def clear_db():
    ExchangeItem.objects.all().delete()

    VehicleLocation.objects.all().delete()
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
            exceptions.FieldError,
            "Невозможно выполнить экспорт значения:"
        ):
            VehicleResource().export()

    def test_import_vehicle(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()
        dataset_model = ModelResource().export()
        dataset_vehicle = VehicleResource().export()

        clear_db()
        self.assertEqual(0, Vehicle.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        ModelResource().import_data(dataset_model, raise_errors=True)
        VehicleResource().import_data(dataset_vehicle, raise_errors=True)

        self.assertEqual(1, Vehicle.objects.all().count())

    def test_vehicle_import_raises_error_if_enterprise_exchange_uuid_is_missing(self):
        self.assertEqual(1, TimeZone.objects.all().count())
        self.assertEqual(1, Enterprise.objects.all().count())

        dataset_time_zone = TimeZoneResource().export()
        EnterpriseResource().export()
        dataset_model = ModelResource().export()
        dataset_vehicle = VehicleResource().export()

        clear_db()
        self.assertEqual(0, Vehicle.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        # EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        ModelResource().import_data(dataset_model, raise_errors=True)

        
        with self.assertRaisesMessage(
            exceptions.ImportError,
            "Невозможно выполнить импорт ссылки:"
        ):
            VehicleResource().import_data(dataset_vehicle, raise_errors=True)        

        self.assertEqual(0, Vehicle.objects.all().count())

    def test_vehicle_import_only_once(self):
        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()
        dataset_model = ModelResource().export()
        dataset_vehicle = VehicleResource().export()

        clear_db()
        self.assertEqual(0, Vehicle.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        ModelResource().import_data(dataset_model, raise_errors=True)
        VehicleResource().import_data(dataset_vehicle, raise_errors=True)

        self.assertEqual(1, Vehicle.objects.all().count())

        VehicleResource().import_data(dataset_vehicle, raise_errors=True)
        self.assertEqual(1, Vehicle.objects.all().count())

    def test_import_enterprise_updates_existing_object(self):
        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()
        dataset_model = ModelResource().export()
        dataset_vehicle = VehicleResource().export()

        clear_db()
        self.assertEqual(0, Vehicle.objects.all().count())

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        ModelResource().import_data(dataset_model, raise_errors=True)
        VehicleResource().import_data(dataset_vehicle, raise_errors=True)        

        exchange_uuid, price, year_of_manufacture, mileage, number, vin, model, enterprise = dataset_vehicle[0]
        self.assertTrue(Vehicle.objects.filter(vin=vin).exists())

        new_vin = "1"*len(vin)

        new_dataset_vehicle = tablib.Dataset([exchange_uuid, price, year_of_manufacture, mileage, number, new_vin, model, enterprise], headers=dataset_vehicle.headers)

        VehicleResource().import_data(new_dataset_vehicle, raise_errors=True)

        self.assertFalse(Vehicle.objects.filter(vin=vin).exists())
        self.assertTrue(Vehicle.objects.filter(vin=new_vin).exists())


class ExchangeVehicleLocationTest(TestCase):
    def setUp(self):
        self.time_zone_data = {
            "code": "UTC",
            "utc_offset": 0,
        }

        time_zone = TimeZone.objects.create(**self.time_zone_data)

        self.enterprise1_data = {
            "name": "enterprise1",
            "city": "city",
            "time_zone": time_zone,
        }

        self.enterprise1 = Enterprise.objects.create(**self.enterprise1_data)

        self.model1_data = {
            "name": "model1",
            "type": "PCR",
            "number_of_seats": 5,
            "tank_capacity_l": 20,
            "load_capacity_kg": 500,
        }

        model1 = Model.objects.create(**self.model1_data)

        self.vehicle1_data = {
            "model": model1,
            "number": "num1",
            "vin": "Z948741AA12323456",
            "year_of_manufacture": 2025,
            "mileage": 100,
            "enterprise": self.enterprise1,
            "price": 125000,
        }

        vehicle1 = Vehicle.objects.create(**self.vehicle1_data)


        self.vehicle_location1_data = {
            "enterprise":self.enterprise1,
            "vehicle": vehicle1,
            "location": Point(37.6173, 55.7558, srid=4326),
            "tracked_at": datetime(2026, 3, 10, 10, 30, 0, tzinfo=UTC),
        }
        VehicleLocation.objects.create(**self.vehicle_location1_data)

        self.vehicle_location2_data = {
            "enterprise":self.enterprise1,
            "vehicle": vehicle1,
            "location": Point(37.6173, 55.7558, srid=4326),
            "tracked_at": datetime(2026, 3, 12, 12, 30, 0, tzinfo=UTC),
        }
        VehicleLocation.objects.create(**self.vehicle_location2_data)
 
    
    def test_export_import_vehicle_location(self):
        dataset_time_zone = TimeZoneResource().export()
        dataset_enterprise = EnterpriseResource().export()
        dataset_model = ModelResource().export()
        dataset_vehicle = VehicleResource().export() 

        dataset_vehicle_location = VehicleLocationResource().export()

        self.assertEqual(2, VehicleLocation.objects.all().count())
        self.assertEqual(1, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())

        clear_db()

        TimeZoneResource().import_data(dataset_time_zone, raise_errors=True)
        EnterpriseResource().import_data(dataset_enterprise, raise_errors=True)
        ModelResource().import_data(dataset_model, raise_errors=True)
        VehicleResource().import_data(dataset_vehicle, raise_errors=True)    

        self.assertEqual(0, VehicleLocation.objects.all().count())
        self.assertEqual(0, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())

        VehicleLocationResource().import_data(dataset_vehicle_location, raise_errors=True)  

        self.assertEqual(2, VehicleLocation.objects.all().count())
        self.assertEqual(1, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())


    def test_export_import_vehicle_location_with_target_cleanup(self):
        TimeZoneResource().export()
        EnterpriseResource().export()
        ModelResource().export()
        VehicleResource().export() 

        period_from = datetime(2026, 3, 10, 10, 0, 0, tzinfo=UTC)
        period_to = datetime(2026, 3, 10, 11, 0, 0, tzinfo=UTC)

        dataset_vehicle_location = VehicleLocationResource().export_data_for_enterprise_and_period(
            self.enterprise1,
            period_from,
            period_to,
            )

        self.assertEqual(2, VehicleLocation.objects.all().count())
        self.assertEqual(1, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())

        empty_dataset_vehicle_location = tablib.Dataset(
            headers=dataset_vehicle_location.headers
        )


        self.assertEqual(2, VehicleLocation.objects.all().count())
        self.assertEqual(1, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())

        empty_dataset_vehicle_location = tablib.Dataset(
            headers=dataset_vehicle_location.headers
        )
        VehicleLocationResource().clear_and_import_data_for_enterprise_and_period(
            empty_dataset_vehicle_location,
            self.enterprise1,
            period_from,
            period_to,
            raise_errors=True
            )


        self.assertEqual(1, VehicleLocation.objects.all().count())
        self.assertEqual(0, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())


        VehicleLocationResource().clear_and_import_data_for_enterprise_and_period(
            dataset_vehicle_location,
            self.enterprise1,
            period_from,
            period_to,
            raise_errors=True
            )  
        
        self.assertEqual(2, VehicleLocation.objects.all().count())
        self.assertEqual(1, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())


        VehicleLocationResource().clear_and_import_data_for_enterprise_and_period(
            dataset_vehicle_location,
            self.enterprise1,
            period_from,
            period_to,
            raise_errors=True
            )  
        
        self.assertEqual(2, VehicleLocation.objects.all().count())
        self.assertEqual(1, VehicleLocation.objects.filter(tracked_at=self.vehicle_location1_data["tracked_at"]).count())




