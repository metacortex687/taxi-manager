from django.urls import path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    path('',RedirectView.as_view(url='/enterprises/',permanent = True)),
    path("vehicles/<int:pk>/edit/",views.vehicle_edit, name="vehicle_edit"),
    path("vehicles/<int:pk>/trips/",views.vehicle_trips, name="vehicle_trips"),
    path("vehicles/new/",views.vehicle_new, name="vehicle_new"),
    path("enterprises/<int:pk>/vehicles/",views.vehicles, name="vehicles"),
    path("enterprises/<int:pk>/edit/",views.enterprise_edit, name="enterprise_edit"),
    path("enterprises/",TemplateView.as_view(template_name="enterprises.html"), name="enterprises"),
    path("login/",TemplateView.as_view(template_name="login.html"), name="login_manager"),
]