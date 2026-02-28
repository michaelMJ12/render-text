from django.contrib import admin
from .models import (
    AttendanceCorrection,
    AttendanceDevice,
    AttendanceDispute,
    AttendanceLog,
    DeviceAlert,
    FingerprintProfile,
    AttendanceEvent,
    AttendanceRecord,
    AttendancePolicy,
    WorkShift,
    CustomAbstractBaseUser
)
from django.contrib.auth.admin import UserAdmin 



@admin.register(AttendanceDevice)
class AttendanceDeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "location", "is_active", "last_seen","ip_address", "api_key", "activation_code", "created_at")
    search_fields = ("name", "device_id", "activated_code")
    list_filter = ("is_active",)



@admin.register(FingerprintProfile)
class FingerprintProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "biometric_id", "device", "is_active")
    search_fields = ("biometric_id", "user__email")
    list_filter = ("device", "is_active")



@admin.register(AttendanceEvent)
class AttendanceEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "device", "timestamp", "source")
    search_fields = (
        "user__email",
        "device__device_id",
    )
    list_filter = ("event_type", "device", "timestamp")
    readonly_fields = ("user", "device", "timestamp", "event_type", "source")
    ordering = ("-timestamp",)

    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "status", "check_in", "check_out")
    search_fields = ("user__email",)
    list_filter = ("status", "date")
    readonly_fields = ("user", "date", "status", "check_in", "check_out")
    ordering = ("-date",)


    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    


class AttendanceDisputeAdmin(admin.ModelAdmin):
    list_display = (
        "attendance_log", 
        "request_by", 
        "reason", 
        "proposed_timestamp", 
        "proposed_event_type", 
        "status", 
        "reviewed_by", 
        "reviewed_at", 
        "admin_comment",
        "created_at"
        )
    search_fields = ("status", "attendance_log__event_type")
    list_filter = ("status", "created_at", "attendance_log")
    readonly_fields = ("created_at",) 




@admin.register(DeviceAlert)
class DeviceAlertAdmin(admin.ModelAdmin):
    list_display = ("device", "message", "is_resolved", "created_at")
    list_filter = ("is_resolved", "device")
    search_fields = ("device__device_name", "message")
    ordering = ("-created_at",)
    list_editable = ("is_resolved",)



@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ("user", "device", "event_type", "timestamp", "source")
    list_filter = ("event_type", "source", "device")
    search_fields = ("user__email", "device__device_name")
    ordering = ("-timestamp",)



@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(admin.ModelAdmin):
    list_display = ("attendance_log", "corrected_event_type", "corrected_timestamp", "approved_by", "created_at")
    list_filter = ("corrected_event_type", "approved_by")
    search_fields = ("attendance_log__user__email",)
    ordering = ("-corrected_timestamp",)



@admin.register(AttendanceDispute)
class AttendanceDisputeAdmin(admin.ModelAdmin):
    list_display = ("attendance_log", "requested_by", "status", "proposed_event_type", "proposed_timestamp", "reviewed_by", "reviewed_at")
    list_filter = ("status", "proposed_event_type", "requested_by", "reviewed_by")
    search_fields = ("attendance_log__user__email", "reason", "admin_comment")
    ordering = ("-created_at",)
    readonly_fields = ("reviewed_by", "reviewed_at", "admin_comment")




admin.site.register(AttendancePolicy)
admin.site.register(WorkShift)



@admin.register(CustomAbstractBaseUser)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_admin",
        "is_superuser",
        "is_student"
    )
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_admin",
        "is_superuser", 
        "is_student"
    )
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("last_login",)

    fieldsets = (
        (("Personal Info"), {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "password",
                "role",
            )
        }),
        (("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_admin",
                "is_student",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        (("Important Dates"), {
            "fields": ("last_login",),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "first_name",
                "last_name",
                "email",
                "role",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_admin",
                "is_superuser",
            ),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")
