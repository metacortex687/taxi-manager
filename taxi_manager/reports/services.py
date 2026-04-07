import uuid

class ReportService():
    def create_report(self, report_type, params) -> uuid.UUID:
        return uuid.uuid4()

