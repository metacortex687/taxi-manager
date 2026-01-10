from django.urls import path
from .views import VehicleListAPIView

urlpatterns = [
    path('vehicles/<int:pk>/', VehicleDetailAPIView.as_view()),
]