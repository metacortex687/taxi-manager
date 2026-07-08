"""
WSGI Django settings.

Используется для:
- WSGI/uWSGI сервиса;
- manage.py команд;
- тестов;
- task-worker.

Для WSGI оставляем persistent DB connections.
"""

import os

from .settings_base import *  # noqa: F403,F401

WSGI_CONN_MAX_AGE = int(os.getenv("WSGI_CONN_MAX_AGE", "600"))

DATABASES = {
    **DATABASES,  # noqa: F405
    "default": {
        **DATABASES["default"],  # noqa: F405
        "CONN_MAX_AGE": WSGI_CONN_MAX_AGE,
    },
}

AUTO_CLEAR_CACHE_ON_SQL_WRITE = True
