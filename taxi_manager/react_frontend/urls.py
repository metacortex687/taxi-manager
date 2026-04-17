from django.urls import path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    path("",views.hello, name="hello_word"),
]