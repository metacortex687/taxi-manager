from rest_framework.views import exception_handler
from django import VERSION as DJANGO_VERSION
from rest_framework import exceptions


def is_invalid_credentials(detail):
    non_field_errors = detail.get("non_field_errors")

    if not non_field_errors:
        return False

    for error in non_field_errors:
        if error.code == "invalid_credentials":
            return True

    return False


def custom_exception_handler(exc, context):
    if isinstance(exc, exceptions.NotAuthenticated): #Исправление проблемы то что исключение NotAuthenticated возвращало 403, а не 401.
        exc = exceptions.NotAuthenticated(*(exc.args))

    if isinstance(exc, exceptions.ValidationError) and is_invalid_credentials(
        exc.detail
    ): # Код возврата когда ошибки учетных данных при получении токена, должен быть 401 а не 403
        exc = exceptions.AuthenticationFailed(*(exc.args))

    return exception_handler(exc, context)