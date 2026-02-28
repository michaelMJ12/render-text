from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from AtendanceApp.services.device_health import get_device_health, get_offline_devices
from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminDeviceHealthView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        health_data = get_device_health()
        offline_devices = get_offline_devices()

        return Response({
            "devices": health_data,
            "offline_count": len(offline_devices),
            "offline_devices": offline_devices
        })
    



    
