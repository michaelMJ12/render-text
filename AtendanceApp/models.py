from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth import get_user_model
import secrets
from django.utils.timezone import now
from django.conf import settings


# Create your models here.

class CustomBaseUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_admin(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "Admin")
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)

        return self.create_user(email, password, **extra_fields)

    def create_staff(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "Staff")
        extra_fields.setdefault("is_staff", True)

        return self.create_user(email, password, **extra_fields)

    def create_student(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "Student")
        extra_fields.setdefault("is_student", True)

        return self.create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "Superuser")
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)



class CustomAbstractBaseUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = (
        ("Admin", "admin"),
        ("Staff", "staff"),
        ("Student", "student"),
        ("Superuser", "superuser"),
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default="Student"
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    objects = CustomBaseUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class AttendanceDevice(models.Model):
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    last_seen = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    api_key = models.CharField(max_length=64, unique=True, editable=False)
    activation_code = models.CharField(max_length=12, unique=True)

    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        if not self.activation_code:
            self.activation_code = secrets.token_hex(6).upper()
        super().save(*args, **kwargs)


    def mark_seen(self, ip=None):
        self.last_seen = now()
        if ip:
            self.ip_address = ip
        self.save(update_fields=["last_seen", "ip_address"])    
   


class FingerprintProfile(models.Model):
    user = models.ForeignKey(CustomAbstractBaseUser, on_delete=models.CASCADE)
    device = models.ForeignKey(AttendanceDevice, on_delete=models.CASCADE)
    biometric_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "device")



class AttendanceEvent(models.Model):
    user = models.ForeignKey(CustomAbstractBaseUser, on_delete=models.CASCADE)
    device = models.ForeignKey(AttendanceDevice, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        choices=[("IN", "Check-in"), ("OUT", "Check-out")],
        max_length=10
    )
    source = models.CharField(default="FINGERPRINT", max_length=50)

    def __str__(self):
        return f"{self.event_type} {self.source}"



class AttendanceRecord(models.Model):
    user = models.ForeignKey(CustomAbstractBaseUser, on_delete=models.CASCADE)
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        choices=[
            ("PRESENT", "Present"),
            ("ABSENT", "Absent"),
            ("LATE", "Late"),
            ("HALF_DAY", "Half Day"),
        ],
        max_length=20
    )


    def __str__(self):
        return f"{self.status}"



class AttendancePolicy(models.Model):
    id = models.AutoField(primary_key=True)
    late_grace_minutes = models.IntegerField(default=10)
    half_day_hours = models.FloatField(default=4.0)
    allow_multiple_checkins = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.late_grace_minutes} {self.half_day_hours}"



class WorkShift(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomAbstractBaseUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    late_after = models.TimeField()



class DeviceAlert(models.Model):
    device = models.ForeignKey(
        AttendanceDevice,
        on_delete=models.CASCADE,
        related_name="alerts"
    )
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.device_name} - {self.message}"



class AttendanceLog(models.Model):
    EVENT_CHOICES = (
        ("IN", "Check In"),
        ("OUT", "Check Out"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device = models.ForeignKey(AttendanceDevice, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField()
    event_type = models.CharField(max_length=3, choices=EVENT_CHOICES)
    source = models.CharField(default="FINGERPRINT", max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.event_type} @ {self.timestamp}"        



class AttendanceCorrection(models.Model):
    Choice = (
        ("IN", "Check In"), 
        ("OUT", "Check Out")
        )
    attendance_log = models.OneToOneField(
        AttendanceLog, on_delete=models.CASCADE, related_name="correction"
    )

    corrected_timestamp = models.DateTimeField(auto_now_add=True)
    corrected_event_type = models.CharField(
        max_length=3, choices=Choice
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correction for Log #{self.attendance_log.id}"




class AttendanceDispute(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    attendance_log = models.ForeignKey(
        AttendanceLog,
        on_delete=models.CASCADE,
        related_name="disputes"
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    reason = models.TextField()

    proposed_timestamp = models.DateTimeField()
    proposed_event_type = models.CharField(
        max_length=20,
        choices=AttendanceLog.EVENT_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_disputes"
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']





# class AttendanceDispute(models.Model):
#     STATUS_CHOICES = (
#         ('PENDING', 'Pending'),
#         ('APPROVED', 'Approved'),
#         ('REJECTED', 'Rejected'),
#     )

#     attendance_log = models.ForeignKey(
#         AttendanceLog,
#         on_delete=models.CASCADE,
#         related_name='disputes'
#     )

#     requested_by = models.ForeignKey(
#         CustomAbstractBaseUser,
#         on_delete=models.CASCADE
#     )

#     reason = models.TextField()

#     proposed_check_in = models.DateTimeField(null=True, blank=True)
#     proposed_check_out = models.DateTimeField(null=True, blank=True)

#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='PENDING'
#     )

#     reviewed_by = models.ForeignKey(
#         CustomAbstractBaseUser,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='reviewed_disputes'
#     )

#     reviewed_at = models.DateTimeField(null=True, blank=True)
#     admin_comment = models.TextField(null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']





