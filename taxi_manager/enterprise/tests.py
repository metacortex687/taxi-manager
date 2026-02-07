from django.test import TestCase
from django.core.management import call_command
from .models import Enterprise

class CommandGenerateDataTest(TestCase):
    def test_generate_one_enterprise(self):
        name_enterprise = "test_name"

        self.assertFalse(Enterprise.objects.filter(name=name_enterprise).exists())

        call_command("generate_data", enterprise = name_enterprise)

        self.assertTrue(Enterprise.objects.filter(name=name_enterprise).exists())


    def test_generate_enterprises(self):
        name_enterprise = ["test_name1", "test_name2"]

        self.assertFalse(Enterprise.objects.filter(name=name_enterprise).exists())

        call_command("generate_data", enterprise = name_enterprise)

        self.assertTrue(Enterprise.objects.filter(name=name_enterprise[0]).exists())
        self.assertTrue(Enterprise.objects.filter(name=name_enterprise[1]).exists())