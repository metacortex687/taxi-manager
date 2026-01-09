from django.urls import path
from .views import VehicleListAPIView

urlpatterns = [
    path('vehicel/', VehicleListAPIView.as_view()),
]