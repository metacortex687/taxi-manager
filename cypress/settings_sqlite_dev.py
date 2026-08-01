from taxi_manager.infrastructure.settings_base import *  # noqa: F403,F401

print("from ..taxi_manager.infrastructure.settings_base import * ")

AUTO_CLEAR_CACHE_ON_SQL_WRITE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': '/dev/shm/cypress_tests.sqlite3',  
    }
}

SPATIALITE_LIBRARY_PATH = "/usr/lib/x86_64-linux-gnu/mod_spatialite.so"

INSTALLED_APPS.remove("django_pgwatch")
INSTALLED_APPS.remove("taxi_manager.infrastructure.vk_bot")
