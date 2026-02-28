# from rest_framework import serializers
# from django.db.models.functions import Coalesce
# from Atendance.AtendanceApp.models import AttendanceLog



# class AttendanceLogSerializer(serializers.ModelSerializer):
#     effective_timestamp = serializers.DateTimeField(read_only=True)
#     effective_event_type = serializers.CharField(read_only=True)

#     class Meta:
#         model = AttendanceLog
#         fields = [
#             "id",
#             "user",
#             "device",
#             "effective_timestamp",
#             "effective_event_type",
#             "source",
#         ]
