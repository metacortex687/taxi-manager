from django.urls import path, include
from .views import VehicleListAPIView, ModelListAPIView, VehicleDetailAPIView, ModelDetailAPIView, DriverListAPIView, DriverDetailAPIView, EnterpriseDetailAPIView, EnterpriseListAPIView

urlpatterns = [
    path("logout/", SessionLogoutView.as_view()),
]