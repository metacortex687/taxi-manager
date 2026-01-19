from django.urls import path, include
from .views import VehicleListAPIView, ModelListAPIView, VehicleDetailAPIView, ModelDetailAPIView, DriverListAPIView, DriverDetailAPIView, EnterpriseDetailAPIView, EnterpriseListAPIView

urlpatterns = [
    path('vehicles/', VehicleListAPIView.as_view()),
    path('models/', ModelListAPIView.as_view()),
    path('vehicles/<int:pk>/', VehicleDetailAPIView.as_view()),
    path('models/<int:pk>/', ModelDetailAPIView.as_view()),
    path('drivers/', DriverListAPIView.as_view()),
    path('enterprises/', EnterpriseListAPIView.as_view()),
    path('drivers/<int:driver_id>/vehicles/', VehicleListAPIView.as_view()),
    path('drivers/<int:pk>/', DriverDetailAPIView.as_view()),
    path('enterprises/<int:pk>/', EnterpriseDetailAPIView.as_view()),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]