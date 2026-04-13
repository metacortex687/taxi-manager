from django.tasks import task
import uuid
import time

@task(queue_name="reports")
def build_report(report_type, report_uuid: str):
    from taxi_manager.reports import services

    report_service = services.ReportService()

    report = report_service.get_report_by_uuid(report_type, uuid.UUID(report_uuid).hex)
    #time.sleep(10)  # даёт время увидеть статус 
    report.status = "PROCESSING"
    report.save(update_fields=["status"])
    #time.sleep(10) # даёт время увидеть статус 
    report.create_values()

    report.status = "DONE"
    report.save(update_fields=["status"])
