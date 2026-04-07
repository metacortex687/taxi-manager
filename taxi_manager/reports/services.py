import uuid
from . import models


class ReportService:
    def create_report(self, report_type, params) -> uuid.UUID:
        return uuid.uuid4()

    def get_available_reports(self):
        [
            {
                "name": report_type["name"],
                "verbose_name": report_type["verbose_name"],
                "params": report_type["params"],
            }
            for report_type in models.Report.get_report_types()
        ]
