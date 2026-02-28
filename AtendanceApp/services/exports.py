import csv
from django.http import HttpResponse
from openpyxl import Workbook
from AtendanceApp.models import AttendanceEvent


def export_attendance_csv(queryset=None):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "User Email",
        "Device ID",
        "Event Type",
        "Timestamp",
        "Source"
    ])

    qs = queryset if queryset is not None else AttendanceEvent.objects.all()

    for event in qs.select_related("user", "device").order_by("-timestamp"):
        writer.writerow([
            event.user.email,
            event.device.device_id if event.device else "N/A",
            event.event_type,
            event.timestamp,
            event.source
        ])

    return response



def export_attendance_excel(queryset=None):
    """
    Export AttendanceEvent queryset to Excel file (.xlsx)
    """
    qs = queryset if queryset is not None else AttendanceEvent.objects.all().select_related("user", "device").order_by("-timestamp")

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance Records"

    # Header row
    ws.append(["User Email", "Device ID", "Event Type", "Timestamp", "Source"])

    # Data rows
    for event in qs:
        ws.append([
            event.user.email,
            event.device.device_id if event.device else "N/A",
            event.event_type,
            event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            event.source
        ])

    # Prepare response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="attendance.xlsx"'
    wb.save(response)
    return response