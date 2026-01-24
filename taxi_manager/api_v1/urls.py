from django.urls import path, include, re_path
from .views import (
    VehicleListAPIView,
    ModelListAPIView,
    VehicleDetailAPIView,
    ModelDetailAPIView,
    DriverListAPIView,
    DriverDetailAPIView,
    EnterpriseDetailAPIView,
    EnterpriseListAPIView,
    SessionLogoutView,
)


urlpatterns = [
    path("vehicles/", VehicleListAPIView.as_view()),
    path("models/", ModelListAPIView.as_view()),
    path("vehicles/<int:pk>/", VehicleDetailAPIView.as_view()),
    path("models/<int:pk>/", ModelDetailAPIView.as_view()),
    path("drivers/", DriverListAPIView.as_view()),
    path("enterprises/", EnterpriseListAPIView.as_view()),
    path("drivers/<int:driver_id>/vehicles/", VehicleListAPIView.as_view()),
    path("drivers/<int:pk>/", DriverDetailAPIView.as_view()),
    path("enterprises/<int:pk>/", EnterpriseDetailAPIView.as_view()),
    # path("logout/", SessionLogoutView.as_view()),
    path(r"auth/", include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    # path("auth/", include('dj_rest_auth.urls')),
]
