from rest_framework import generics, permissions
from AtendanceApp.models import AttendanceLog
from AtendanceApp.serializer import AttendanceDisputeSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication



class AttendanceDisputeCreateView(
    generics.CreateAPIView, 
    generics.DestroyAPIView,
    generics.ListAPIView, 
    generics.RetrieveAPIView):
    serializer_class = AttendanceDisputeSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        log = AttendanceLog.objects.get(pk=self.kwargs['log_id'])
        serializer.save(
        attendance_log=log,
        requested_by=self.request.user
        )
