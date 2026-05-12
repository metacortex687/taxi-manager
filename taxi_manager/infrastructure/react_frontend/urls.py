from django.urls import re_path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    re_path(
        r"^(?!api/|admin/|vjs/|site/|static/|media/)(?P<subpath>.*)$",
        views.index,
        name="index_react",
    ),
]