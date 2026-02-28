from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from AtendanceApp.services.dashboard import get_admin_attendance_dashboard





class AdminAttendanceDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = get_admin_attendance_dashboard()
        return Response(data)
