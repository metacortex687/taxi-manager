from django.urls import re_path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    re_path(r"^(?P<subpath>.*)$", views.index, name="index_react"),
]