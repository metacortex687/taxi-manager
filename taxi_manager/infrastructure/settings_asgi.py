"""
ASGI Django settings.

Используется только ASGI/gunicorn+uvicorn сервисом.

Для ASGI + PgBouncer не держим клиентские DB-соединения долго,
иначе PgBouncer накапливает idle client connections и упирается в max_client_conn.
"""

import os

from .settings_base import *  # noqa: F403,F401

DATABASES = {
    **DATABASES,  # noqa: F405
    "default": {
        **DATABASES["default"],  # noqa: F405
        "CONN_MAX_AGE": 0,
    },
}

AUTO_CLEAR_CACHE_ON_SQL_WRITE = False