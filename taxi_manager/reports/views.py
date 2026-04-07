from rest_framework.views import APIView
from rest_framework.response import Response

from . import models


class ReportListAPIView(APIView):
    def get(self, request):
        return Response(
            [
                {
                    "name": report_type["name"],
                    "verbose_name": report_type["verbose_name"],
                }
                for report_type in models.Report.get_report_types()
            ]
        )
