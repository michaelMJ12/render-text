from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from AtendanceApp.models import AttendanceDispute
from AtendanceApp.services.attendance_dispute import review_dispute
from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminDisputeReviewView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, dispute_id):
        dispute = AttendanceDispute.objects.get(id=dispute_id)

        action = request.data.get("action")  # APPROVE / REJECT
        comment = request.data.get("comment")

        review_dispute(
            dispute=dispute,
            admin_user=request.user,
            approve=(action == "APPROVE"),
            comment=comment
        )

        return Response({"status": dispute.status})
