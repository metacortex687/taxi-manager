from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from ..api_v1.views import VehicleViewSet
from ..enterprise.models import Enterprise


class VehicleAPITest(TestCase):
    def setUp(self):
        enterprise1 = Enterprise.objects.create(
            name="enterprise1", city="city"
        )


        self.user = get_user_model().objects.create_user(
            username="user", email="test@mail.com", password="secret"
        )

        self.superuser = get_user_model().objects.create_user(
            username="super_user", email="test@mail.com", password="secret", is_superuser=True
        )

        self.manager1 = get_user_model().objects.create_user(
            username="manager1", email="manager1@mail.com", password="secret"
        )
        self.manager1.managed_enterprises.add(enterprise1)

        self.viewset_get_list = VehicleViewSet.as_view({"get": "list"})

    def test_anonymous_cannot_list_return_403(self):

        factory = APIRequestFactory()
        request = factory.get("/api/v1/vehicles/")

        responce = self.viewset_get_list(request)

        self.assertEqual(responce.status_code, 403)


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