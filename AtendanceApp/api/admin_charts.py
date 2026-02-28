from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from AtendanceApp.services.charts import daily_attendance_trend


class AdminAttendanceChartsView(APIView):
    permission_classes = [IsAdminUser,IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        days = int(request.GET.get("days", 7))
        data = daily_attendance_trend(days=days)
        return Response({
            "daily_trend": data
        })
