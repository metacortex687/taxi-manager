from django.urls import path, include
from . import views


urlpatterns = [
    path("index/", views.index),
    path("test_csrf_protect/", views.test_csrf_protect),
]