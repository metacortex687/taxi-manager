"""
URL configuration for taxi_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vjs/", include("taxi_manager.infrastructure.vanilla_frontend.urls")),
    path("api/v1/", include("taxi_manager.infrastructure.api_v1.urls")),
    path("site/", include("taxi_manager.infrastructure.simply_site.urls")),    
]

if settings.PROFILER_SILK_ENBLE:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]

if settings.DEBUG_TOOLBAR_ENABLE:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()

urlpatterns += [
    path("", include("taxi_manager.infrastructure.react_frontend.urls")),
]