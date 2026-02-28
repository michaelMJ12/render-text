# AtendanceApp/api/attendance_ingest.py

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from AtendanceApp.models import AttendanceDevice

class FingerprintIngestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        device_id = request.data.get("device_id")

        device = AttendanceDevice.objects.filter(
            device_id=device_id,
            is_active=True
        ).first()

        if not device:
            return Response({"error": "Invalid device"}, status=400)

        # ✅ HEALTH UPDATE (THIS IS KEY)
        device.last_seen = timezone.now()
        device.save(update_fields=["last_seen"])

        # continue attendance processing...
        return Response({"status": "attendance recorded"})
