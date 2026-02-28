from datetime import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer , TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from .models import AttendanceDevice,AttendanceDispute, AttendanceLog,FingerprintProfile,AttendanceEvent,AttendanceRecord,AttendancePolicy,WorkShift, CustomAbstractBaseUser
User = get_user_model()





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['is_active'] = user.is_active
        token['role'] = (
            'Admin' if user.is_admin else 
            'Superuser' if user.is_superuser else
            'Staff' if user.is_staff else 'User'

        )

        return token
    


    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'first_name' : self.user.first_name,
            'last_name' : self.user.last_name,
            'email' : self.user.email,
            'role' : (
                'Admin' if self.user.is_admin else 
                'Staff' if self.user.is_staff else 
                'Superuser' if self.user.is_superuser else 'User'
            )
        }

        return data
        


class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        token = RefreshToken(attrs['refresh'])
        user_id = token['user_id']
        
        User = get_user_model()

        user = User.objects.get(id=user_id)

        data['user'] = {
            'first_name':user.first_name,
            'last_name':user.last_name,
            'email' :user.email,
            'role': (
                'Admin'if user.is_admin else 
                'Staff'if user.is_staff else
                'Superuser' if user.is_superuser else 'User'
            )
        }

        return data



class LogoutUserSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            RefreshToken(value)
        except Exception:
            raise serializers.ValidationError('Invalid token')
        return value

    def save(self, **kwargs):
        RefreshToken(self.validated_data['refresh']).blacklist()
        



class CustomeSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        refesh = RefreshToken.for_user(user)
        access = refesh.access_token

        return {
            'access':str(access),
            'refresh':str(refesh),
            'user': {
                'first_name':user.first_name,
                'last_name':user.last_name,
                'email':user.email,
                'role':(
                    'Admin' if user.is_admin else
                    'Staff' if user.is_staff else
                    'Superuser' if user.is_superuser else 'User'
                )
            }
        }




class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    class Meta:
        model = CustomAbstractBaseUser
        fields = (
            "first_name",
            "last_name",
            "email",
            "role",
            "password",
            "is_active",
            "is_staff",
            "is_admin",
            "is_student",
        )
        read_only_fields = ("is_active", "is_staff", "is_admin", "is_student")

    def validate_email(self, value):
        if CustomAbstractBaseUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('User exist already.') 

        return value   

    def create(self, validated_data):

        role = validated_data.get('role', 'Student')

        if role == 'Admin':
            validated_data['is_admin'] = True

        if role == 'Student':
            validated_data['is_student'] = True

        if role == 'Staff':
            validated_data['is_staff'] = True    
       
        password = validated_data.pop('password')
        user = CustomAbstractBaseUser.objects.create_user(
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user


class AttendanceDeviceSerializer(serializers.ModelSerializer):  
    class Meta:
        model = AttendanceDevice
        fields = "__all__"
        read_only_field = "__all__"



class FingerprintProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FingerprintProfile
        fields = "__all__"
        read_only_fields = "__all__"




class AttendanceEventSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    device_name = serializers.CharField(write_only=True)

    class Meta:
        model = AttendanceEvent
        fields = "__all__"
        read_only_fields = "__all__"




class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = "__all__"        
        


class AttendancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendancePolicy
        fields = "__all__"        


class WorkShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkShift
        fields = "__all__"


class FingerprintPayloadSerializer(serializers.Serializer):
    biometric_id = serializers.CharField(max_length=100)
    device_id = serializers.CharField(max_length=100)
    timestamp = serializers.DateTimeField()
    event_type = serializers.ChoiceField(choices=["IN", "OUT"])


class MonthlyAttendanceReportSerializer(serializers.Serializer):
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    half_day = serializers.IntegerField()
    total_days = serializers.IntegerField()


class FingerprintEnrollmentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    biometric_id = serializers.CharField(max_length=100)



class DeviceRegistrationSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)



# class AttendanceDisputeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AttendanceDispute
#         fields = [
#             "attendance_log",
#             "reason",
#             "proposed_timestamp",
#             "proposed_event_type",
#         ]

#     def validate(self, attrs):
#         log = attrs["attendance_log"]
#         proposed_type = attrs["proposed_event_type"]

#         # Optional but VERY good validation
#         if proposed_type not in dict(AttendanceLog.EVENT_CHOICES):
#             raise serializers.ValidationError("Invalid event type")

#         return attrs


class AttendanceDisputeSerializer(serializers.ModelSerializer):

    def validate_attendance_log(self, log):
        user = self.context['request'].user
        if log.user != user:
            raise serializers.ValidationError(
                "You can only dispute your own attendance logs."
            )
        return log

    class Meta:
        model = AttendanceDispute
        fields = [
            'attendance_log',
            'reason',
            'proposed_timestamp',
            'proposed_event_type'
        ]



class AttendanceLogSerializer(serializers.ModelSerializer):
    effective_timestamp = serializers.DateTimeField(read_only=True)
    effective_event_type = serializers.CharField(read_only=True)
    class Meta:
        model = AttendanceLog
        fields = [
            "id",
            "user",
            "device",
            "effective_timestamp",
            "effective_event_type",
            "source",
        ]


class DeviceActivationSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    activation_code = serializers.CharField()
