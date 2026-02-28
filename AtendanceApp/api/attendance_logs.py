from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from django.db.models.functions import Coalesce
from AtendanceApp.serializer import AttendanceLogSerializer
from AtendanceApp.models import AttendanceLog




class AttendanceLogViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AttendanceLogSerializer

    def get_queryset(self):
        return AttendanceLog.objects.annotate(
            effective_timestamp=Coalesce(
                "correction__corrected_timestamp",
                "timestamp",
            ),
            effective_event_type=Coalesce(
                "correction__corrected_event_type",
                "event_type",
            ),
        )
