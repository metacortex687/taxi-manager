from rest_framework.views import exception_handler
from django import VERSION as DJANGO_VERSION
from rest_framework import exceptions


def custom_exception_handler(exc, context):
    if isinstance(exc, exceptions.NotAuthenticated): #Исправление проблемы то что исключение NotAuthenticated возвращало 403, а не 401.
        exc = exceptions.NotAuthenticated(*(exc.args))

    return exception_handler(exc, context)