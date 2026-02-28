from django.shortcuts import render,get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from AtendanceApp.services.dashboard import get_admin_attendance_dashboard
from AtendanceApp.permission import IsAdmin
from .serializer import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, DeviceActivationSerializer, DeviceRegistrationSerializer, FingerprintEnrollmentSerializer , LogoutUserSerializer, CustomeSocialLoginSerializer,CustomUserSerializer,AttendanceDeviceSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.views import status
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework.decorators import permission_classes,api_view
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet
from .models import AttendanceDevice, FingerprintProfile,AttendanceEvent,AttendanceRecord,AttendancePolicy,WorkShift,CustomAbstractBaseUser
from .serializer import FingerprintProfileSerializer,AttendanceEventSerializer,AttendanceRecordSerializer,AttendancePolicySerializer,WorkShiftSerializer,FingerprintPayloadSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.utils.timezone import localdate
from django.db.models import Count
from .serializer import MonthlyAttendanceReportSerializer
from .services.attendance_broadcast import broadcast_attendance
from AtendanceApp.services.attendance_rules import is_duplicate_scan
from AtendanceApp.services.attendance_policy import evaluate_attendance
from AtendanceApp.services.device_auth import verify_device_signature
from django.utils.timezone import now
from django.http import HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
import secrets
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import AuthenticationFailed, NotFound





class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer



class LogoutUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer_object = LogoutUserSerializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        serializer_object.save()
        return Response({
            'success':'logout is successful.',
        }, status=status.HTTP_204_NO_CONTENT)



class CustomSocialLoginView(SocialLoginView):
    serializer_class = CustomeSocialLoginSerializer
    adapter_class = GoogleOAuth2Adapter



class CustomUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [JWTAuthentication]
    def post(self,request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success":"User created successful.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    

    def get(self, request, id=None):
        if id is not None:
            try:
                user = CustomAbstractBaseUser.objects.get(id=id)
                serializer = CustomUserSerializer(instance=user)
                return Response({
                "success": f"User with id:{id} fetched successfully.",
                "data": serializer.data
                }, status=status.HTTP_200_OK)

            except CustomAbstractBaseUser.DoesNotExist:
                return Response({
                "error": f"User with id:{id} not found."
                }, status=status.HTTP_404_NOT_FOUND)
            
       
        queryset = CustomAbstractBaseUser.objects.all()
        pagenator = PageNumberPagination()
        pagenator.page_size = 5
        pagenated_query = pagenator.paginate_queryset(queryset, request)
        serializer = CustomUserSerializer(instance=pagenated_query, many=True)
        return pagenator.get_paginated_response({
            "success": "All users fetched successfully.",
            "data": serializer.data
        })
    
    def put(self, request, id):
        try:
            queryDic = CustomAbstractBaseUser.objects.get(id=id)
            serializer = CustomUserSerializer(instance=queryDic, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "success":f"User with id:{id} is successful updated.",
                "data":serializer.data
            }, status=status.HTTP_200_OK)
        except CustomAbstractBaseUser.DoesNotExist :
            return Response({
                "error":f"User with id:{id} dose not exist."
            },status=status.HTTP_404_NOT_FOUND)
        
    
    def delete(self, request, id):
        try:
            queryDic = get_object_or_404(CustomAbstractBaseUser, id=id)
            queryDic.delete()
            return Response({
                "success":f"User with id:{id} is deleted successful."
            }, status=status.HTTP_204_NO_CONTENT)
        except CustomAbstractBaseUser.DoesNotExist:
            return Response({
                "error":f"User with id:{id} not found."
            },status=status.HTTP_404_NOT_FOUND)
 



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        serializer = CustomUserSerializer(instance=request.user)
        return Response({
            "success":"user profile fetch successful.",
            "data":serializer.data
        }, status=status.HTTP_200_OK)
    


class AttendanceDeviceViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AttendanceDevice.objects.all()
    serializer_class = AttendanceDeviceSerializer


class FingerprintProfileViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = FingerprintProfile.objects.all()
    serializer_class = FingerprintProfileSerializer

    

class AttendanceEventViewSet(ReadOnlyModelViewSet):
    queryset = AttendanceEvent.objects.all().order_by("-timestamp")
    serializer_class = AttendanceEventSerializer



class AttendanceRecordViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer


class AttendancePolicyViewSet(ModelViewSet):
    queryset = AttendancePolicy.objects.all()
    serializer_class = AttendancePolicySerializer


class WorkShiftViewSet(ModelViewSet):
    queryset = WorkShift.objects.all()
    serializer_class = WorkShiftSerializer



class FingerprintIngestView(APIView):
    authentication_classes = []   
    

    def post(self, request):
        # ================================
        # 0️⃣ Validate payload
        # ================================
        serializer = FingerprintPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # ================================
        # 1️⃣ DEVICE AUTH (API KEY + HMAC)
        # ================================
        device_id = request.headers.get("X-DEVICE-ID")
        api_key = request.headers.get("X-API-KEY")
        signature = request.headers.get("X-SIGNATURE")

        if not all([device_id, api_key, signature]):
            return Response(
                {"message": "Missing device authentication headers"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            device = AttendanceDevice.objects.get(
                device_id=device_id,
                api_key=api_key,
                is_active=True
            )
            device.mark_seen()
        except AttendanceDevice.DoesNotExist:
            return Response(
                {"message": "Invalid device credentials"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not verify_device_signature(device, data, signature):
            return Response(
                {"message": "Invalid signature"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ================================
        # 2️⃣ Fingerprint validation
        # ================================
        try:
            profile = FingerprintProfile.objects.get(
                biometric_id=data["biometric_id"],
                device=device,
                is_active=True
            )
        except FingerprintProfile.DoesNotExist:
            return Response(
                {"message": "Unknown or inactive fingerprint"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = profile.user
        timestamp = data["timestamp"]
        event_type = data["event_type"]

        # ================================
        # 3️⃣ Anti-duplicate protection
        # ================================
        if is_duplicate_scan(user, device, event_type, timestamp):
            return Response(
                {"message": "Duplicate scan ignored"},
                status=status.HTTP_200_OK
            )

        # ================================
        # 4️⃣ Immutable event log
        # ================================
        AttendanceEvent.objects.create(
            user=user,
            device=device,
            timestamp=timestamp,
            event_type=event_type
        )

        broadcast_attendance(user, event_type, timestamp)

        # ================================
        # 5️⃣ Attendance record (daily)
        # ================================
        record, _ = AttendanceRecord.objects.get_or_create(
            user=user,
            date=localdate(timestamp),
            defaults={"status": "PRESENT"}
        )

        if event_type == "IN" and not record.check_in:
            record.check_in = timestamp

        if event_type == "OUT":
            record.check_out = timestamp

        record.save()

        # ================================
        # 6️⃣ Apply policy AFTER checkout
        # ================================
        if event_type == "OUT":
            policy = AttendancePolicy.objects.first()
            shift = WorkShift.objects.first()

            if policy and shift:
                evaluate_attendance(record, shift, policy)

        return Response(
            {"message": "Attendance recorded successfully"},
            status=status.HTTP_201_CREATED
        )



class MonthlyAttendanceReportView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")
        month = int(request.query_params.get("month"))
        year = int(request.query_params.get("year"))

        qs = AttendanceRecord.objects.filter(
            user_id=user_id,
            date__month=month,
            date__year=year
        )

        data = {
            "present": qs.filter(status="PRESENT").count(),
            "absent": qs.filter(status="ABSENT").count(),
            "late": qs.filter(status="LATE").count(),
            "half_day": qs.filter(status="HALF_DAY").count(),
            "total_days": qs.count(),
        }

        serializer = MonthlyAttendanceReportSerializer(data)
        return Response({
            "success":f"successful monthly report",
            "data":serializer.data
        }, status=status.HTTP_200_OK)
    



# class AdminAttendanceDashboardView(APIView):
#     permission_classes = [IsAdminUser]

#     def get(self, request):
#         today = now().date()

#         stats = AttendanceRecord.objects.filter(date=today).values(
#             "status"
#         ).annotate(count=Count("id"))

#         response = {
#             "date": today,
#             "summary": {
#                 "present": 0,
#                 "absent": 0,
#                 "late": 0,
#                 "half_day": 0,
#             }
#         }

#         for item in stats:
#             key = item["status"].lower()
#             response["summary"][key] = item["count"]

#         return Response(response)



# class Home(APIView):
#     authentication_classes = []  
#     permission_classes = []

#     def get(self, request):
#         return Response(
#             {'message': 'Api view response'},
#             status=status.HTTP_200_OK
#         )

 
class AdminCreateDeviceView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = DeviceRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        device = AttendanceDevice.objects.create(
            device_id=serializer.validated_data["device_id"],
            name=serializer.validated_data["name"],
            location=serializer.validated_data["location"],
            is_active=False  # 🔐 locked until activation
        )

        return Response(
            {
                "device_id": device.device_id,
                "activation_code": device.activation_code,
                "status": "CREATED",
                "message": "Device created. Awaiting activation."
            },
            status=status.HTTP_201_CREATED
        )

    


class FingerprintEnrollmentView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = FingerprintEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        device_id = request.headers.get("X-DEVICE-ID")
        api_key = request.headers.get("X-API-KEY")

        if not device_id or not api_key:
            raise AuthenticationFailed("Missing device credentials")

        # 🔐 Authenticate device FIRST
        try:
            device = AttendanceDevice.objects.get(
                device_id=device_id,
                api_key=api_key,
                is_active=True
            )
        except AttendanceDevice.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive device")

        # 👤 Get user
        try:
            user = CustomAbstractBaseUser.objects.get(email=data["email"])
        except CustomAbstractBaseUser.DoesNotExist:
            raise NotFound("User not found")

        # 🧬 Enroll fingerprint (device is guaranteed to exist here)
        profile, created = FingerprintProfile.objects.get_or_create(
            user=user,
            device_id=device.device_id,
            email=data['email'],
            defaults={"biometric_id": data["biometric_id"]}
        )

        if not created:
            profile.biometric_id = data["biometric_id"]
            profile.is_active = True
            profile.save()

        return Response(
            {
                "email": user.email,
                "biometric_id": profile.biometric_id,
                "created": created
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    


class AdminAttendanceDashboardView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        data = get_admin_attendance_dashboard()
        return Response({
            "sucess":f"dashboard record successfuly fetch.",
            "data":data
        })
    


class DeviceActivationView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = DeviceActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            device = AttendanceDevice.objects.get(
                device_id=data["device_id"],
                is_active=False
            )
        except AttendanceDevice.DoesNotExist:
            return Response(
                {"detail": "Invalid or already activated device"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if device.activation_code != data["activation_code"]:
            return Response(
                {"detail": "Invalid activation code"},
                status=status.HTTP_403_FORBIDDEN
            )

        device.is_active = True
        device.ip_address = request.META.get("REMOTE_ADDR")
        device.save(update_fields=["is_active", "ip_address"])

        return Response(
            {
                "device_id": device.device_id,
                "api_key": device.api_key
            },
            status=status.HTTP_200_OK
        )







# class FingerprintEnrollmentView(APIView):

#     def post(self, request):
#         serializer = FingerprintEnrollmentSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data

#         device_id = request.headers.get("X-DEVICE-ID")
#         api_key = request.headers.get("X-API-KEY")

#         device = AttendanceDevice.objects.get(
#             device_id=device_id,
#             api_key=api_key,
#             is_active=True
#         )

#         user = CustomAbstractBaseUser.objects.get(email=data["email"])

#         profile, created = FingerprintProfile.objects.get_or_create(
#             user=user,
#             device_id=device.device_id,
#             defaults={"biometric_id": data["biometric_id"]}
#         )

#         if not created:
#             profile.biometric_id = data["biometric_id"]
#             profile.save()

#         return Response(
#             {
#                 "email": user.email,
#                 "biometric_id": profile.biometric_id,
#                 "created": created
#             },
#             status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
#         )

    

    

# class DeviceRegistrationView(APIView):
#     """
#     Endpoint for network-enabled scanner to register itself.
#     """

#     def post(self, request):
#         data = request.data
#         device_id = data.get("device_id")
#         name = data.get("name")
#         location = data.get("location")
#         ip_address = request.META.get('REMOTE_ADDR')  # device IP

#         if not all([device_id, name, location]):
#             return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

#         device, created = AttendanceDevice.objects.get_or_create(
#             device_id=device_id,
#             defaults={
#                 "name": name,
#                 "location": location,
#                 "ip_address": ip_address,
#                 "api_key": secrets.token_hex(32)
#             }
#         )

#         return Response({
#             "device_id": device.device_id,
#             "api_key": device.api_key,
#             "created": created
#         }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)



# class FingerprintEnrollmentView(APIView):
#     """
#     Endpoint for scanner to enroll a user's fingerprint
#     """
#     authentication_classes = []  # device can use API key header instead
#     permission_classes = []

#     def post(self, request):
#         data = request.data
#         device_id = request.headers.get("X-DEVICE-ID")
#         api_key = request.headers.get("X-API-KEY")

#         # Authenticate device
#         try:
#             device = AttendanceDevice.objects.get(device_id=device_id, api_key=api_key, is_active=True)
#         except AttendanceDevice.DoesNotExist:
#             return Response({"error": "Invalid device"}, status=status.HTTP_403_FORBIDDEN)

#         # Get user info
#         email = data.get("email")
#         biometric_id = data.get("biometric_id")
#         if not all([email, biometric_id]):
#             return Response({"error": "Missing email or biometric_id"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             user = CustomAbstractBaseUser.objects.get(email=email)
#         except CustomAbstractBaseUser.DoesNotExist:
#             return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

#         # Create fingerprint profile
#         profile, created = FingerprintProfile.objects.get_or_create(
#             user=user,
#             device_id=device.device_id,
#             defaults={"biometric_id": biometric_id, "is_active": True}
#         )

#         if not created:
#             profile.biometric_id = biometric_id
#             profile.is_active = True
#             profile.save()

#         return Response({
#             "user": user.email,
#             "biometric_id": profile.biometric_id,
#             "created": created
#         }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)