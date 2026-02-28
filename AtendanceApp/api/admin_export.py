from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from AtendanceApp.models import AttendanceEvent
from AtendanceApp.services.exports import export_attendance_csv, export_attendance_excel


class AdminAttendanceExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = AttendanceEvent.objects.all()

        # Optional filters
        start_date = request.GET.get("start")
        end_date = request.GET.get("end")
        event_type = request.GET.get("event_type")

        if start_date and end_date:
            qs = qs.filter(timestamp__date__range=[start_date, end_date])

        if event_type:
            qs = qs.filter(event_type=event_type)

        return export_attendance_csv(qs)



class AdminAttendanceExportExcelView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = AttendanceEvent.objects.all()

        # Optional filters
        start_date = request.GET.get("start")
        end_date = request.GET.get("end")
        event_type = request.GET.get("event_type")

        if start_date and end_date:
            qs = qs.filter(timestamp__date__range=[start_date, end_date])

        if event_type:
            qs = qs.filter(event_type=event_type)

        return export_attendance_excel(qs)