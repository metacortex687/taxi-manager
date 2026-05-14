from dataclasses import asdict

from rest_framework.decorators import api_view
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response

from taxi_manager.application.use_cases.enterprise_manager_usecase import (
    EnterpriseManagerUseCase,
)
from taxi_manager.domain.entities.manager import ManagerId
from taxi_manager.infrastructure.repositories.enterprise_manager_django_rep import (
    EnterpriseManagerDjangoRep,
)
from taxi_manager.infrastructure.repositories.time_zone_django_rep import (
    TimeZoneDjangoRep,
)


@api_view(["GET"])
def enterprise_list_view(request):
    user = request.user

    if user.is_anonymous:
        raise NotAuthenticated("Авторизуйтесь")

    uc = EnterpriseManagerUseCase(
        enterprise_manager_assigment_rep=EnterpriseManagerDjangoRep(),
        time_zone_rep=TimeZoneDjangoRep(),
    )

    enterprises = uc.get_manager_assigments(ManagerId(user.id))

    return Response({"results": [asdict(enterprise) for enterprise in enterprises]})