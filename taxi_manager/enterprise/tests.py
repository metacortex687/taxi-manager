from django.test import TestCase
from django.core.management import call_command
from .models import Enterprise
from taxi_manager.vehicle.models import Driver, Model
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

        
    # def test_generate_enterprises(self):
    #     name_enterprise = ["test_name1", "test_name2"]

    #     self.assertFalse(Enterprise.objects.filter(name=name_enterprise).exists())

    #     call_command("generate_data", enterprise = name_enterprise, driver = 5)

    #     self.assertTrue(Enterprise.objects.filter(name=name_enterprise[0]).exists())
    #     self.assertTrue(Enterprise.objects.filter(name=name_enterprise[1]).exists())