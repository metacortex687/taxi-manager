from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from ..api_v1.views import VehicleViewSet
from ..enterprise.models import Enterprise
from ..vehicle.models import Model, Vehicle


class VehicleAPITest(TestCase):
    def setUp(self):
        self.enterprise1 = Enterprise.objects.create(name="enterprise1", city="city")
        self.enterprise2 = Enterprise.objects.create(name="enterprise2", city="city")
        self.enterprise3 = Enterprise.objects.create(name="enterprise3", city="city")

        self.user = get_user_model().objects.create_user(
            username="user", email="test@mail.com", password="secret"
        )

        self.superuser = get_user_model().objects.create_user(
            username="super_user",
            email="test@mail.com",
            password="secret",
            is_superuser=True,
        )

        self.manager1 = get_user_model().objects.create_user(
            username="manager1", email="manager1@mail.com", password="secret"
        )
        self.manager1.managed_enterprises.add(self.enterprise1)
        self.manager1.managed_enterprises.add(self.enterprise2)

        self.model1 = Model.objects.create(
            name="model1",
            type="PCR",
            number_of_seats=5,
            tank_capacity_l=20,
            load_capacity_kg=500,
        )

        self.vehicle1 = Vehicle.objects.create(
            model=self.model1,
            number="num1",
            vin="Z948741AA12323456",
            year_of_manufacture=2025,
            mileage=100,
            enterprise=self.enterprise1,
            price=125000,
        )

        self.vehicle3 = Vehicle.objects.create(
            model=self.model1,
            number="num3",
            vin="Z234741AA12323456",
            year_of_manufacture=2025,
            mileage=100,
            enterprise=self.enterprise3,
            price=125000,
        )

        self.viewset_get_list = VehicleViewSet.as_view({"get": "list"})
        self.viewset_post_create = VehicleViewSet.as_view({"post": "create"})
        self.viewset_put_update = VehicleViewSet.as_view({"put": "update"})
        self.viewset_delete_destroy = VehicleViewSet.as_view({"delete": "destroy"})
        self.viewset_get_retrieve = VehicleViewSet.as_view({"get": "retrieve"})

    def test_anonymous_cannot_list_return_401(self):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/vehicles/")

        responce = self.viewset_get_list(request)

        self.assertEqual(responce.status_code, 401)

    def test_not_manager_cannot_list_return_403(self):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/vehicles/")

        force_authenticate(request, user=self.user)
        responce = self.viewset_get_list(request)

        self.assertTrue(self.superuser.is_superuser)
        self.assertEqual(responce.status_code, 403)

    def test_manager_can_list_return_200(self):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/vehicles/")

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_get_list(request)

        self.assertEqual(responce.status_code, 200)

    def test_manager_can_create_vehicle_for_managed_enterprise_return_201(self):
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise1.pk,
                "price": 1250000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 201)
        self.assertTrue(Vehicle.objects.filter(number="test1").exists())

    def test_manager_cannot_create_vehicle_for_not_managed_enterprise_return_403(self):
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise3.pk,
                "price": 1250000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 403)
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

    def test_anonymous_cannot_create_vehicle_return_401(self):
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise3.pk,
                "price": 1250000,
            },
            format="json",
        )

        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 401)
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

    def test_superuser_cannot_create_vehicle_return_403(self):
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise3.pk,
                "price": 1250000,
            },
            format="json",
        )

        force_authenticate(request, user=self.superuser)
        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 403)
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

    def test_manager_can_update_vehicle_for_managed_enterprise_return_200(self):
        self.vehicle1.refresh_from_db()
        self.assertNotEqual(self.vehicle1.price, 50000000)
        self.assertNotEqual(self.vehicle1.enterprise, self.enterprise3)

        factory = APIRequestFactory()
        request = factory.put(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise2.pk,
                "price": 50000000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_put_update(request, pk=self.vehicle1.pk)

        self.assertEqual(responce.status_code, 200)

        self.vehicle1.refresh_from_db()
        self.assertEqual(self.vehicle1.price, 50000000)
        self.assertEqual(self.vehicle1.enterprise, self.enterprise2)

    def test_manager_can_update_vehicle_for_managed_enterprise_to_unmanged_return_403(
        self,
    ):
        factory = APIRequestFactory()
        request = factory.put(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise3.pk,
                "price": 50000000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_put_update(request, pk=self.vehicle1.pk)

        self.assertEqual(responce.status_code, 403)

    def test_anonymous_cannot_update_vehicle_for_managed_enterprise_to_unmanged_return_401(
        self,
    ):
        factory = APIRequestFactory()
        request = factory.put(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise2.pk,
                "price": 50000000,
            },
            format="json",
        )

        responce = self.viewset_put_update(request, pk=self.vehicle1.pk)


        self.assertEqual(responce.status_code, 401)

    def test_superuser_cannot_update_vehicle_for_managed_enterprise_to_unmanged_return_403(
        self,
    ):
        factory = APIRequestFactory()
        request = factory.put(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise2.pk,
                "price": 50000000,
            },
            format="json",
        )

        force_authenticate(request, user=self.superuser)
        responce = self.viewset_put_update(request, pk=self.vehicle1.pk)

        self.assertEqual(responce.status_code, 403)

    def test_manager_can_delete_vehicle_for_managed_enterprise_return_200(self):
        pk = self.vehicle1.pk
        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())

        factory = APIRequestFactory()
        request = factory.delete(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_delete_destroy(request, pk=self.vehicle1.pk)

        self.assertFalse(Vehicle.objects.filter(pk=pk).exists())
        self.assertEqual(responce.status_code, 204)

    def test_manager_cannot_delete_vehicle_for_unmanaged_enterprise_return_403(self):
        pk = self.vehicle3.pk
        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())

        factory = APIRequestFactory()
        request = factory.delete(
            f"/api/v1/vehicles/{self.vehicle3.pk}/",
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_delete_destroy(request, pk=self.vehicle3.pk)

        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())
        self.assertEqual(responce.status_code, 403)

    def test_anonymous_cannot_delete_vehicle_return_401(self):
        pk = self.vehicle3.pk
        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())

        factory = APIRequestFactory()
        request = factory.delete(
            f"/api/v1/vehicles/{self.vehicle3.pk}/",
            format="json",
        )

        responce = self.viewset_delete_destroy(request, pk=self.vehicle3.pk)

        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())
        self.assertEqual(responce.status_code, 401)

    def test_superuser_cannot_delete_vehicle_return_403(self):
        pk = self.vehicle3.pk
        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())

        factory = APIRequestFactory()
        request = factory.delete(
            f"/api/v1/vehicles/{self.vehicle3.pk}/",
            format="json",
        )

        force_authenticate(request, user=self.superuser)
        responce = self.viewset_delete_destroy(request, pk=self.vehicle3.pk)

        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())
        self.assertEqual(responce.status_code, 403)

    def test_manager_can_retrieve_vehicle_for_managed_enterprise_return_200(self):
        factory = APIRequestFactory()
        request = factory.get(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_get_retrieve(request, pk=self.vehicle1.pk)

        self.assertEqual(responce.status_code, 200)

    def test_manager_cannot_retrieve_vehicle_for_unmanaged_enterprise_return_403(self):
        factory = APIRequestFactory()
        request = factory.get(
            f"/api/v1/vehicles/{self.vehicle3.pk}/",
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_get_retrieve(request, pk=self.vehicle3.pk)

        self.assertEqual(responce.status_code, 403)

    def test_anonymous_cannot_retrieve_vehicle_for_unmanaged_enterprise_return_401(
        self,
    ):
        factory = APIRequestFactory()
        request = factory.get(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            format="json",
        )

        responce = self.viewset_get_retrieve(request, pk=self.vehicle1.pk)

        self.assertEqual(responce.status_code, 401)

    def test_superuser_cannot_retrieve_vehicle_for_unmanaged_enterprise_return_403(
        self,
    ):
        factory = APIRequestFactory()
        request = factory.get(
            f"/api/v1/vehicles/{self.vehicle1.pk}/",
            format="json",
        )

        force_authenticate(request, user=self.superuser)
        responce = self.viewset_get_retrieve(request, pk=self.vehicle1.pk)

        self.assertEqual(responce.status_code, 403)
