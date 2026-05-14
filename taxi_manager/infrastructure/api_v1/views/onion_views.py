from dataclasses import asdict

from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from taxi_manager.application.use_cases.enterprise_manager_usecase import (
    EnterpriseManagerUseCase,
)
from taxi_manager.application.use_cases.enterprise_usecase import EnterpriseUseCase
from taxi_manager.domain.entities.enterprise import EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.infrastructure.repositories.enterprise_django_rep import (
    EnterpriseDjangoRep,
)
from taxi_manager.infrastructure.repositories.enterprise_manager_django_rep import (
    EnterpriseManagerDjangoRep,
)
from taxi_manager.infrastructure.repositories.time_zone_django_rep import (
    TimeZoneDjangoRep,
)

enterprise_manager_usecase = EnterpriseManagerUseCase(
    enterprise_manager_assigment_rep=EnterpriseManagerDjangoRep(),
    time_zone_rep=TimeZoneDjangoRep(),
)

enterprise_usecase = EnterpriseUseCase(
    enterprise_rep=EnterpriseDjangoRep(),
    time_zone_rep=TimeZoneDjangoRep(),
)


@api_view(["GET"])
def enterprise_list_view(request):
    user = request.user

    if user.is_anonymous:
        raise NotAuthenticated("Авторизуйтесь")

    enterprises = enterprise_manager_usecase.get_manager_assigments(ManagerId(user.id))

    return Response({"results": [asdict(enterprise) for enterprise in enterprises]})


# @api_view(["GET"])
def enterprise_detail_view_get(request, pk):
    user = request.user

    enterprise_id = EnterpriseId(pk)
    enterprise = enterprise_usecase.get(enterprise_id)

    if not enterprise_manager_usecase.is_assigment_exist(
        ManagerId(user.id), enterprise_id
    ):
        raise PermissionDenied(
            f'У вас нет прав менеджера в "{enterprise.name}"(id={pk})'
        )

    return Response(asdict(enterprise_usecase.get(enterprise_id)))
