from django.urls import path
from .views import VehicleListAPIView

urlpatterns = [
    path('vehicles/', VehicleListAPIView.as_view()),
    path('models/', ModelListAPIView.as_view()),
    path('vehicles/<int:pk>/', VehicleDetailAPIView.as_view()),
    path('models/<int:pk>/', ModelDetailAPIView.as_view()),
]