from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from django.contrib.gis.geos import Point, Polygon

from rest_framework.test import APIRequestFactory, force_authenticate

from taxi_manager.api_v1.views.main import VehicleViewSet
from taxi_manager.enterprise.models import Enterprise
from taxi_manager.vehicle.models import Model, Vehicle, Driver
from taxi_manager.geo_tracking.models import Trip, VehicleLocation
from taxi_manager.time_zones.models import TimeZone
from taxi_manager.geocoding.models import GeoAddress

from datetime import datetime, UTC


class VehicleAPITest(TestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
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

    def get_token(self, user):
        response = self.client.post(
            "/api/v1/auth/token/login/", {"username": "manager1", "password": "secret"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["auth_token"])
        return response.data["auth_token"]

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

    def test_manager_cannot_delete_vehicle_with_driver_return_409(self):
        pk = self.vehicle1.pk
        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())

        driver = Driver.objects.create(
            first_name="first_name_driver1",
            last_name="last_name_driver1",
            TIN="12345",
            enterprise=self.enterprise1,
        )
        self.vehicle1.drivers.add(
            driver, through_defaults={"enterprise": self.enterprise1}
        )

        response = self.client.delete(
            f"/api/v1/vehicles/{pk}/",
            headers={"Authorization": f"Token {self.get_token(self.manager1)}"},
        )

        self.assertEqual(response.status_code, 409)
        self.assertTrue(Vehicle.objects.filter(pk=pk).exists())

        # Если убрать ссылку то удалит
        # self.vehicle1.drivers.remove(driver)
        # response = self.client.delete(
        #     f"/api/v1/vehicles/{pk}/",
        #     headers={"Authorization": f"Token {self.get_token(self.manager1)}"},
        # )
        # self.assertEqual(response.status_code, 409)
        # self.assertFalse(Vehicle.objects.filter(pk=pk).exists())

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

    def test_cannot_create_vehicle_with_short_vin_return_400(self):
        """
        VIN номер в записи об авто не может быть меньше 17 символов
        """

        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR12345",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise1.pk,
                "price": 1250000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 400)
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

    def test_cannot_create_vehicle_with_long_vin_return_400(self):
        """
        VIN номер в записи об авто не может быть длиннее 17 символов
        """

        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "Z948741AACR1234561",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise1.pk,
                "price": 1250000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 400)
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

    def test_cannot_create_vehicle_with_invalid_chars_vin_return_400(self):
        """
        VIN номер может содержать только символы "0 1 2 3 4 5 6 7 8 9 A B C D E F G H J K L M N P R S T U V W X Y Z"
        символы I, O, Q запрещены
        """

        self.assertFalse(Vehicle.objects.filter(number="test1").exists())

        factory = APIRequestFactory()
        request = factory.post(
            "/api/v1/vehicles/",
            {
                "model": self.model1.pk,
                "number": "test1",
                "vin": "IOQ8741AACR123456",
                "year_of_manufacture": 2025,
                "mileage": 100,
                "enterprise": self.enterprise1.pk,
                "price": 1250000,
            },
            format="json",
        )

        force_authenticate(request, user=self.manager1)
        responce = self.viewset_post_create(request)

        self.assertEqual(responce.status_code, 400)
        self.assertFalse(Vehicle.objects.filter(number="test1").exists())


class TokenAPITest(TestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(name="enterprise1", city="city")
        self.manager1 = get_user_model().objects.create_user(
            username="manager1", email="manager1@mail.com", password="secret"
        )
        self.manager1.managed_enterprises.add(self.enterprise1)

    def test_token_login_success_return_200(self):
        """
        Пользователь может авторизоваться, поулчить токен, и с использованием этого токена получить например информацию о своей учетной записи.
        """
        response = self.client.post(
            "/api/v1/auth/token/login/", {"username": "manager1", "password": "secret"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["auth_token"])

        response = self.client.get(
            "/api/v1/auth/users/me/",
            headers={"Authorization": f"Token {response.data['auth_token']}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "manager1")

    def test_token_login_failure_return_401(self):
        """
        В случае если пользователь вводит неправильные учетные данные, то он не может получить токен
        """
        response = self.client.post(
            "/api/v1/auth/token/login/", {"username": "manager1", "password": "wrong"}
        )

        self.assertEqual(response.status_code, 401)

    def test_manager_can_access_vehile_list_with_token_return_200(self):
        """
        Менеджер получив токен, может получить доступ до списка машин.
        """
        response = self.client.post(
            "/api/v1/auth/token/login/", {"username": "manager1", "password": "secret"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["auth_token"])

        response = self.client.get(
            "/api/v1/vehicles/",
            headers={"Authorization": f"Token {response.data['auth_token']}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_cannot_access_vehile_list_with_invalid_token_return_401(self):
        """
        С неправильным токеном, нельзя получить доступ до списка машин. Код возврата 401.
        """

        response = self.client.get(
            "/api/v1/vehicles/", headers={"Authorization": "Token invalid_token"}
        )
        self.assertEqual(response.status_code, 401)

    def test_cannot_access_vehile_list_without_token_return_401(self):
        """
        Без токена, нельзя получить доступ до списка машин. Код возврата 401.
        """

        response = self.client.get("/api/v1/vehicles/")
        self.assertEqual(response.status_code, 401)

    def test_get_unknown_endpoint_return_404(self):
        """
        Без токена, попытка доступа до несуществующего ресурса.
        """

        response = self.client.get("/api/v1/unknown_endpoint/")
        self.assertEqual(response.status_code, 404)


class EnterpriseAPITest(TestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(name="enterprise1", city="city")
        self.enterprise2 = Enterprise.objects.create(name="enterprise2", city="city")
        self.enterprise3 = Enterprise.objects.create(name="enterprise3", city="city")

        self.manager1 = get_user_model().objects.create_user(
            username="manager1", email="manager1@mail.com", password="secret"
        )
        self.manager2 = get_user_model().objects.create_user(
            username="manager2", email="manager1@mail.com", password="secret"
        )

        self.manager1.managed_enterprises.add(self.enterprise1)
        self.manager1.managed_enterprises.add(self.enterprise2)

        self.manager2.managed_enterprises.add(self.enterprise2)
        self.manager2.managed_enterprises.add(self.enterprise3)

        # self.viewset_get_retrieve = EnterpriseDetailAPIView.as_view()

    def get_token(self, user):
        response = self.client.post(
            "/api/v1/auth/token/login/", {"username": "manager1", "password": "secret"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["auth_token"])
        return response.data["auth_token"]

    def test_manager_can_retriev_managed_enterprise_with_token_return_200(self):
        response = self.client.get(
            f"/api/v1/enterprises/{self.enterprise1.pk}/",
            headers={"Authorization": f"Token {self.get_token(self.manager1)}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "enterprise1")

    def test_manager_cannot_retriev_unmanaged_enterprise_with_token_return_403(self):
        response = self.client.get(
            f"/api/v1/enterprises/{self.enterprise3.pk}/",
            headers={"Authorization": f"Token {self.get_token(self.manager1)}"},
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_list_enterprises_returns_only_managed(self):
        response = self.client.get(
            "/api/v1/enterprises/",
            headers={"Authorization": f"Token {self.get_token(self.manager1)}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual({1, 2}, {result["id"] for result in response.data["results"]})

    def test_superuser_lists_only_managed_enterprises(self):
        self.manager1.is_superuser = True
        self.manager1.save()

        response = self.client.get(
            "/api/v1/enterprises/",
            headers={"Authorization": f"Token {self.get_token(self.manager1)}"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual({1, 2}, {result["id"] for result in response.data["results"]})

    def test_user_cannot_retriev_enterprise_without_token_return_401(self):
        response = self.client.get(f"/api/v1/enterprises/{self.enterprise3.pk}/")

        self.assertEqual(response.status_code, 401)

    def test_user_cannot_retriev_enterprise_with_invalid_token_return_401(self):
        response = self.client.get(
            f"/api/v1/enterprises/{self.enterprise3.pk}/",
            headers={"Authorization": "Token invalid_token"},
        )

        self.assertEqual(response.status_code, 401)


class BaseAuthTestCase(TestCase):
    def __init__(self, methodName="runTest"):
        self.passwords = {}

        super().__init__(methodName)

    def create_user(self, username, email, password):
        self.passwords[username] = password

        return get_user_model().objects.create_user(
            username=username, email=email, password=password
        )

    def get_token(self, user):
        response = self.client.post(
            "/api/v1/auth/token/login/",
            {"username": user.username, "password": self.passwords[user.username]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["auth_token"])
        return response.data["auth_token"]
   
    def client_get(self, url, user):
        return self.client.get(url,
            headers={"Authorization": f"Token {self.get_token(user)}"},
        )
    
    def client_post(self, url, user, data):
        return self.client.post(
            url,
            data=data,
            headers={"Authorization": f"Token {self.get_token(user)}"},
        )




class TripPointAPITest(BaseAuthTestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(
            name="enterprise1", city="city", time_zone=self.time_zone
        )

        password = "secret"
        self.manager1 = self.create_user(
            username="manager1", email="manager1@mail.com", password=password
        )

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

        self.trip1 = Trip.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            started_at=datetime(2026, 3, 10, 10, 0, 0, tzinfo=UTC),
            ended_at=datetime(2026, 3, 10, 11, 0, 0, tzinfo=UTC),
        )

        self.location_in_trip = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6173, 55.7558, srid=4326),
            tracked_at=datetime(2026, 3, 10, 10, 30, 0, tzinfo=UTC),
        )

        self.location_not_in_trip = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6180, 55.7560, srid=4326),
            tracked_at=datetime(2026, 3, 10, 11, 30, 0, tzinfo=UTC),
        )

    def test_return_status_code_200(self):
        """
        Получение точек трекинга для поездки работает
        """

        token = self.get_token(self.manager1)

        response = self.client.get(
            f"/api/v1/vehicles/{self.vehicle1.pk}/trip-points/?from=2026-03-01T00:00:00Z&to=2026-03-31T23:59:59Z",
            headers={"Authorization": f"Token {token}"},
        )

        self.assertEqual(response.status_code, 200)

    def test_return_list_points_only_in_trip_200(self):
        token = self.get_token(self.manager1)

        response = self.client.get(
            f"/api/v1/vehicles/{self.vehicle1.pk}/trip-points/?from=2026-03-01T00:00:00Z&to=2026-03-31T23:59:59Z",
            headers={"Authorization": f"Token {token}"},
        )

        self.assertEqual(response.status_code, 200)

        # ожидаем только 1 точку — ту, что попала в Trip
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.location_in_trip.id)

    def test_return_list_points_only_in_trip_utc_plus_3(self):
        token = self.get_token(self.manager1)

        response = self.client.get(
            f"/api/v1/vehicles/{self.vehicle1.pk}/trip-points/?from=2026-03-01T00:00:00%2B03:00&to=2026-03-31T23:59:59%2B03:00",
            headers={"Authorization": f"Token {token}"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], self.location_in_trip.id)


class TripAPITest(BaseAuthTestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(
            name="enterprise1", city="city", time_zone=self.time_zone
        )

        password = "secret"
        self.manager1 = self.create_user(
            username="manager1", email="manager1@mail.com", password=password
        )

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

        self.vehicle2 = Vehicle.objects.create(
            model=self.model1,
            number="num2",
            vin="Z948741AA12322222",
            year_of_manufacture=2025,
            mileage=100,
            enterprise=self.enterprise1,
            price=125000,
        )       

        self.trip1 = Trip.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            started_at=datetime(2026, 3, 10, 10, 0, 0, tzinfo=UTC),
            ended_at=datetime(2026, 3, 10, 11, 0, 0, tzinfo=UTC),
        )

        self.trip2 = Trip.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle2,
            started_at=datetime(2026, 3, 10, 10, 0, 0, tzinfo=UTC),
            ended_at=datetime(2026, 3, 10, 11, 0, 0, tzinfo=UTC),
        )

        self.location_not_in_trip_min = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6173, 55.7558, srid=4326),
            tracked_at=datetime(2026, 3, 10, 9, 15, 0, tzinfo=UTC),
        )

        self.start_point = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6173, 55.7558, srid=4326),
            tracked_at=datetime(2026, 3, 10, 10, 15, 0, tzinfo=UTC),
        )

        self.location_in_trip_average = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6173, 55.7558, srid=4326),
            tracked_at=datetime(2026, 3, 10, 10, 15, 0, tzinfo=UTC),
        )

        self.end_point = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6180, 55.7560, srid=4326),
            tracked_at=datetime(2026, 3, 10, 10, 25, 0, tzinfo=UTC),
        )

        self.location_not_in_trip_max = VehicleLocation.objects.create(
            enterprise=self.enterprise1,
            vehicle=self.vehicle1,
            location=Point(37.6180, 55.7560, srid=4326),
            tracked_at=datetime(2026, 3, 10, 11, 25, 0, tzinfo=UTC),
        )


        self.address1 = "Address1"

        west = 37.6123784
        east = 37.6255645 
        north = 55.7559849
        south = 55.7480273

        polygon = Polygon((
                (west, south),
                (east, south),
                (east, north),
                (west, north),
                (west, south),
            ), srid=4326
        )
        GeoAddress.objects.create(display_name=self.address1, area = polygon)



    def test_list_trips_returns_200_for_manager(self): 
        '''
        Менеджер может получить список поездок автомобиля 
        '''
        response = self.client_get(f"/api/v1/vehicles/{self.vehicle1.pk}/trips/", self.manager1)

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]
        self.assertEqual(len(results),1)


    def test_trip_list_contains_start_point(self): 
        '''
        В информации по поездке есть стартовая точка
        '''
        response = self.client_get(f"/api/v1/vehicles/{self.vehicle1.pk}/trips/", self.manager1)

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results),1)
        self.assertEqual(results[0]["start_point"]["lon"],self.start_point.location.x)
        self.assertEqual(results[0]["start_point"]["lat"],self.start_point.location.y)
        self.assertEqual(results[0]["start_point"]["address"],self.address1)


    def test_trip_list_contains_end_point(self): 
        '''
        В информации по поездке есть последняя точка
        '''
        response = self.client_get(f"/api/v1/vehicles/{self.vehicle1.pk}/trips/", self.manager1)

        self.assertEqual(response.status_code, 200)

        results = response.data["results"]

        self.assertEqual(len(results),1)
        self.assertEqual(results[0]["end_point"]["lon"],self.end_point.location.x)
        self.assertEqual(results[0]["end_point"]["lat"],self.end_point.location.y)
        self.assertIsNotNone(results[0]["end_point"]["address"])


class ReportsTest(BaseAuthTestCase):
    def setUp(self):
        self.time_zone = TimeZone.objects.create(code="UTC", utc_offset=0)
        self.enterprise1 = Enterprise.objects.create(
            name="enterprise1", city="city", time_zone=self.time_zone
        )

        password = "secret"
        self.manager1 = self.create_user(
            username="manager1", email="manager1@mail.com", password=password
        )

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


    def test_list_reports(self):
        response = self.client_get("/api/v1/reports/list/", self.manager1)

        self.assertEqual(response.status_code, 200)

        data = response.data
        self.assertTrue(len(data) > 0)
        self.assertTrue("name" in data[0])
        self.assertTrue("verbose_name" in data[0])
        self.assertTrue("params" in data[0])


    def test_post_report(self):
        response = self.client_post("/api/v1/reports/carmileagereport/", self.manager1, data={"enterprise": self.enterprise1.id, "vehicle": self.vehicle1.id})

        self.assertEqual(response.status_code, 201)

        self.assertTrue("uuid" in response.data)

        




