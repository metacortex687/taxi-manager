from rest_framework import exceptions, status


class DeletionConflict(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = ('Конфликт удаления записи. Есть ссылки на элемент в других записях')
    default_code = 'deletion_conflict'