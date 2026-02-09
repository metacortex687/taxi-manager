from django.test import TestCase
from django.core.management import call_command
from .models import Enterprise
from taxi_manager.vehicle.models import Driver, Model, Vehicle, VehicleDriver
from django.core.management.base import CommandError


class CommandGenerateDataTest(TestCase):
    def test_generate_one_enterprise(self):
        name_enterprise = "test_name"

        self.assertFalse(Enterprise.objects.filter(name=name_enterprise).exists())

        call_command("generate_data", enterprise=name_enterprise, driver=5, vehicle=20)

        self.assertTrue(Enterprise.objects.filter(name=name_enterprise).exists())

    def test_generate_enterprises(self):
        name_enterprise = ["test_name1", "test_name2"]

        self.assertFalse(Enterprise.objects.filter(name=name_enterprise).exists())

        call_command("generate_data", enterprise=name_enterprise, driver=5, vehicle=20)

        self.assertTrue(Enterprise.objects.filter(name=name_enterprise[0]).exists())
        self.assertTrue(Enterprise.objects.filter(name=name_enterprise[1]).exists())

    def test_raises_when_enterprise_option_missing(self):
        with self.assertRaises(CommandError):
            call_command("generate_data", driver=5, vehicle=20)

    def test_raises_when_driver_option_missing(self):
        with self.assertRaises(CommandError):
            call_command("generate_data", enterprise=["ent1", "ent2"], vehicle=20)

    def test_generate_one_driver(self):
        name_enterprise = "test_name"

        self.assertFalse(Driver.objects.exists())

        call_command("generate_data", enterprise=name_enterprise, driver=1, vehicle=20)

        self.assertEqual(Driver.objects.count(), 1)

    def test_generate_7_driver(self):
        name_enterprise = "test_name"

        self.assertFalse(Driver.objects.exists())

        call_command("generate_data", enterprise=name_enterprise, driver=7, vehicle=20)

        self.assertEqual(Driver.objects.count(), 7)

    def test_generate_5_model(self):
        name_enterprise = "test_name"

        self.assertFalse(Model.objects.exists())

        call_command("generate_data", enterprise=name_enterprise, driver=7, vehicle=20)

        self.assertEqual(Model.objects.count(), 5)

    def test_raises_when_vehicle_option_missing(self):
        with self.assertRaises(CommandError):
            call_command("generate_data", enterprise=["ent1", "ent2"], driver=5)

    def test_generate_one_vehicle(self):
        name_enterprise = "test_name"

        self.assertFalse(Vehicle.objects.exists())

        call_command("generate_data", enterprise=name_enterprise, driver=1, vehicle=1)

        self.assertEqual(Vehicle.objects.count(), 1)

    def test_generate_15_vehicle(self):
        name_enterprise = "test_name"

        self.assertFalse(Vehicle.objects.exists())

        call_command("generate_data", enterprise=name_enterprise, driver=1, vehicle=15)

        self.assertEqual(Vehicle.objects.count(), 15)

    def test_generate_links_of_vehicles_and_drivers(self):
        name_enterprise = ["test_name1", "test_name2", "test_name3"]
        call_command("generate_data", enterprise=name_enterprise, driver=15, vehicle=51, seed=24) 

        self.assertTrue(VehicleDriver.objects.exists())
        self.assertEqual(VehicleDriver.objects.count(), 171) #Для seed=24 171 оно должно быть большим


    def test_generate_set_active_links_of_vehicles_and_drivers_when_one_enterprise_and_fewer_vehicles_then_driver(self):
        name_enterprise = ["test_name1"]
        call_command("generate_data", enterprise=name_enterprise, driver=150, vehicle=51, seed=24) 

        self.assertEqual(VehicleDriver.objects.filter(active=True).count(), 6)  #6 а не 5 так как уменьшил вероятность авто без машин и водителей без авто

    def test_generate_set_active_links_of_vehicles_and_drivers_when_one_enterprise_and_more_vehicles_then_driver(self):
        name_enterprise = ["test_name1"]
        call_command("generate_data", enterprise=name_enterprise, driver=3, vehicle=51, seed=24) 

        self.assertEqual(Vehicle.objects.count(), 51) 
        self.assertEqual(Driver.objects.count(), 3) 
        self.assertEqual(VehicleDriver.objects.filter(active=True).count(), 3) #3 а не 2 так как уменьшил вероятность авто без машин и водителей без авто

    
    def test_generate_more_data(self):
        name_enterprise = ["test_name1"]
        call_command("generate_data", enterprise=name_enterprise, driver=100, vehicle=1000, seed=15) 

        self.assertEqual(Vehicle.objects.count(), 1000) 
        self.assertEqual(Driver.objects.count(), 100) 
        self.assertEqual(VehicleDriver.objects.count(), 3600) #Числа случайные для seed=15, важен прорядок чисел
        self.assertEqual(VehicleDriver.objects.values("driver").distinct().count(), 91) #Числа случайные для seed=15, важен прорядок чисел
        self.assertEqual(VehicleDriver.objects.values("vehicle").distinct().count(), 907) #Числа случайные для seed=15, важен прорядок чисел
        self.assertEqual(VehicleDriver.objects.filter(active=True).count(), 91) #Числа случайные для seed=15, важен прорядок чисел

    def test_generate_links_vehicle_driver_for_all_enterprises(self):
        name_enterprise = ["test_name1","test_name2","test_name3","test_name4","test_name5"]
        call_command("generate_data", enterprise=name_enterprise, driver=100, vehicle=1000, seed=15) 

        self.assertEqual(VehicleDriver.objects.values("enterprise").distinct().count(), len(name_enterprise))
        self.assertEqual(Driver.objects.values("enterprise").distinct().count(), len(name_enterprise))
        self.assertEqual(Vehicle.objects.values("enterprise").distinct().count(), len(name_enterprise))
