from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from . import services


class ReportListAPIView(APIView):
    def get(self, request):
        return Response(services.ReportService().get_available_reports())


class ReportAPIView(APIView):
    def post(self, request, report_type):
        params = dict(self.request.data)
        uuid = services.ReportService().create_report(report_type, params, request.user)

        return Response(
            {
                "uuid": str(uuid),
                "type": report_type,
                "status": "done",
                "params": params,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request, report_type, uuid=None):
        report_service = services.ReportService()

        if uuid is None:
            return Response(
                {
                    "params": report_service.get_params_value(report_type, request.user),
                    "headers": report_service.get_result_headers(report_type),
                }
            )

        return Response(
            {
                "uuid": str(uuid),
                "result": report_service.get_result(report_type, uuid),
            },
        )
