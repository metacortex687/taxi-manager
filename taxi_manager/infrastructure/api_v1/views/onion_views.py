from dataclasses import asdict

from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.response import Response

from taxi_manager.application.enterprise_manager_assignment.usecase import (
    EnterpriseManagerUseCase,
)
from taxi_manager.application.enterprise.usecase import EnterpriseUseCase
from taxi_manager.domain.entities.enterprise import Enterprise, EnterpriseId
from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.domain.entities.time_zone import TimeZoneId
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

# @api_view(["PUT"])
def enterprise_detail_view_put(request, pk):
    user = request.user

    enterprise_id = EnterpriseId(pk)
    enterprise = enterprise_usecase.get(enterprise_id)

    if not enterprise_manager_usecase.is_assigment_exist(
        ManagerId(user.id), enterprise_id
    ):
        raise PermissionDenied(
            f'У вас нет прав менеджера в "{enterprise.name}"(id={pk})'
        )
    

    enterprise_to_update = Enterprise(
        id = enterprise_id,
        name = request.data["name"],
        city = request.data["city"],
        time_zone_id = TimeZoneId(request.data["time_zone"])        
    ) 

    enterprise_usecase.update(enterprise_to_update)

    enterprise = enterprise_usecase.get(enterprise_id)
    return Response(asdict(enterprise_usecase.get(enterprise_id)))


def enterprise_detail_view_delete(request, pk):
    user = request.user

    enterprise_id = EnterpriseId(pk)
    enterprise = enterprise_usecase.get(enterprise_id)

    manager_id = ManagerId(user.id)

    if not enterprise_manager_usecase.is_assigment_exist(
        manager_id, enterprise_id
    ):
        raise PermissionDenied(
            f'У вас нет прав менеджера в "{enterprise.name}"(id={pk})'
        )   
    
    if len(enterprise_manager_usecase.get_enterprise_assigments(enterprise_id)) > 1:
        return Response(status=409)

    enterprise_manager_usecase.delete(enterprise_id, manager_id)

    enterprise_usecase.delete(enterprise_id)

    return Response(status=204)


@api_view(["GET", "PUT", "DELETE"])
def enterprise_detail_view(request, pk):
    if request.method == "GET":
        return enterprise_detail_view_get(request, pk)

    if request.method == "PUT":
        return enterprise_detail_view_put(request, pk)

    if request.method == "DELETE":
        return enterprise_detail_view_delete(request, pk)


