from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser, SAFE_METHODS

@api_view(["POST"])
def trigger_sql_error(request):
    """
    Намеренно выполняет некорректный SQL-запрос
    для проверки журналирования и мониторинга ошибок.
    """
    with connection.cursor() as cursor:
        # FR0M написано с нулём намеренно.
        cursor.execute("SELECT * FR0M monitoring_sql_error")


@api_view(["POST"])
def trigger_application_error(request):
    """
    Намеренно вызывает исключение для проверки
    журналирования и мониторинга ошибок приложения.
    """
    raise RuntimeError("Intentional application error for monitoring test")
