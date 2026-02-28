from django.urls import path, include
from rest_framework.routers import DefaultRouter
from AtendanceApp.api.admin_disputes import AdminDisputeReviewView
from AtendanceApp.api.attendance_disputes import AttendanceDisputeCreateView
from AtendanceApp.api.admin_device_health import AdminDeviceHealthView
from AtendanceApp.api.admin_export import AdminAttendanceExportExcelView, AdminAttendanceExportView
from AtendanceApp.api.admin_charts import AdminAttendanceChartsView
from AtendanceApp.api.admin_dashboard import AdminAttendanceDashboardView




from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutUserView,
    CustomSocialLoginView,
    CustomUserView,
    UserProfileView,
    MonthlyAttendanceReportView,
    FingerprintIngestView,
    AttendanceDeviceViewSet,
    AttendancePolicyViewSet,
    AttendanceEventViewSet,
    AttendanceRecordViewSet,
    FingerprintProfileViewSet,
    WorkShiftViewSet,
    AdminCreateDeviceView,
    FingerprintEnrollmentView,
    DeviceActivationView,
)

router = DefaultRouter()


router.register(r'api/device', AttendanceDeviceViewSet, basename='device')
router.register(r'api/policy', AttendancePolicyViewSet, basename='policy')
router.register(r'api/event', AttendanceEventViewSet, basename='event')
router.register(r'api/record', AttendanceRecordViewSet, basename='record')
router.register(r'api/fingerprint-profile', FingerprintProfileViewSet, basename='fingerprint-profile')
router.register(r'api/shift', WorkShiftViewSet, basename='shift')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'api/auth/login', 
        CustomTokenObtainPairView.as_view(), 
        name='token_obtain_pair'
        ),
    path(
        'api/auth/refresh', 
        CustomTokenRefreshView.as_view(),
          name='refresh_token'
          ),
    path(
        'api/auth/logout', 
        LogoutUserView.as_view(), 
        name='logout'
        ),
    path(
        'api/auth/social',
          CustomSocialLoginView.as_view(), 
          name='social_google_account'
          ),
    path(
        'api/auth/signup', 
        CustomUserView.as_view(), 
        name='signup'
        ),
    path(
        'api/auth/signup/<int:id>', 
        CustomUserView.as_view(), 
        name='signup'
        ),
    path(
        'api/auth/profile', 
        UserProfileView.as_view(), 
        name='profile'
        ),
    path(
        'api/fingerprint', 
        FingerprintIngestView.as_view(), 
        name='payload'
        ),
    path(
        'api/report/monthly', 
        MonthlyAttendanceReportView.as_view(), 
        name='report'
        ),
    path(
        'api/register/device', 
        AdminCreateDeviceView.as_view(), 
        name='device'
        ),
    path(
        "api/admin/dashboard",
        AdminAttendanceDashboardView.as_view(),
        name="admin-attendance-dashboard"
    ),
    path(
        "api/admin/charts",
        AdminAttendanceChartsView.as_view(),
        name="admin-attendance-charts"
    ),
    
    path(
        "api/fingerprint/enroll",
        FingerprintEnrollmentView.as_view(),
        name='enroll'
    ),

    path(
        "api/admin/export/attendance/csv",
        AdminAttendanceExportView.as_view(),
        name="admin-attendance-export"
    ),

     path(
        "api/admin/export/attendance/excel",
        AdminAttendanceExportExcelView.as_view(),
        name="admin-attendance-export-excel"
    ),

    path(
        "api/admin/devices/health",
        AdminDeviceHealthView.as_view(),
        name="admin-device-health"
    ),

   path(
       "api/attendance/logs/<int:log_id>/dispute",
        AttendanceDisputeCreateView.as_view(),
        name="attendance-dispute-create"
    ),

    path("api/admin/attendance/disputes/<int:dispute_id>/review", AdminDisputeReviewView.as_view()),
    path("api/device/activate", DeviceActivationView.as_view(), name="activate")

]
