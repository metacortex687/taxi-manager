from django.urls import path, include, re_path
from .views import (
    VehicleViewSet,
    ModelListAPIView,
    ModelDetailAPIView,
    DriverListAPIView,
    DriverDetailAPIView,
    EnterpriseDetailAPIView,
    EnterpriseListAPIView,
    TimeZoneListAPIView,
    VehicleLocationListAPIView,
    TripPointListAPIView,
    TripListAPIView,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet)

urlpatterns = [
    path("", include(router.urls)),

    path("drivers/<int:driver_id>/vehicles/", VehicleViewSet.as_view({"get":"list"})),
    path("drivers/<int:pk>/", DriverDetailAPIView.as_view()),
    path("drivers/", DriverListAPIView.as_view()),
    
    path("models/", ModelListAPIView.as_view()),
    path("models/<int:pk>/", ModelDetailAPIView.as_view()),  

    path("enterprises/<int:enterprise_id>/vehicles/", VehicleViewSet.as_view({"get":"list"})),
    path("enterprises/<int:enterprise_id>/drivers/", DriverListAPIView.as_view()),
    # path("enterprises/<int:enterprise_id>/trips/", DriverListAPIView.as_view()),
    path("enterprises/<int:pk>/", EnterpriseDetailAPIView.as_view()),
    path("enterprises/", EnterpriseListAPIView.as_view()),

    path("timezones/", TimeZoneListAPIView.as_view()),

    path("vehicles/<int:vehicle_id>/locations/", VehicleLocationListAPIView.as_view()),
    path("vehicles/<int:vehicle_id>/trip-points/", TripPointListAPIView.as_view()),
    path("vehicles/<int:vehicle_id>/trips/", TripListAPIView.as_view()),
    

    # path("logout/", SessionLogoutView.as_view()),
    path(r"auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.authtoken")),
    # path("auth/", include('dj_rest_auth.urls')),
]
