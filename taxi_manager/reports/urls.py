from django.urls import path
from django.views.generic import TemplateView, RedirectView
from . import views

urlpatterns = [
    path("list/",views.ReportListAPIView.as_view()),
    path("<str:report_type>/",views.ReportAPIView.as_view()),
]