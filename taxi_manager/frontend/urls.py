from django.urls import path
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('',RedirectView.as_view(url='/enterprises/',permanent = True)),
    path("enterprises/",TemplateView.as_view(template_name="enterprises.html"), name="enterprises"),
    path("login/",TemplateView.as_view(template_name="login.html"), name="login_manager"),
]