from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import models
from . import services


class ReportListAPIView(APIView):
    def get(self, request):
        return Response(
            [
                {
                    "name": report_type["name"],
                    "verbose_name": report_type["verbose_name"],
                    "params": report_type["params"],
                }
                for report_type in models.Report.get_report_types()
            ]
        )


class ReportAPIView(APIView):
    def post(self, request, report_type):
        params = self.request.data.dict()
        uuid = services.ReportService().create_report(report_type, params)

        return Response(
            {"uuid": str(uuid), "type": report_type, "status": "done", "params": params},
            status=status.HTTP_201_CREATED
        )
