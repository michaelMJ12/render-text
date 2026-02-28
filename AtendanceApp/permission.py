from .models import CustomAbstractBaseUser
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ParseError





class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'Admin':
            raise PermissionDenied("Only Admin is allowed")
        return True


class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'Staff':
            raise PermissionDenied('Only Staff is allowed.')
        return True
    

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if request.user.role != 'Student':
            raise PermissionDenied('Only Student allowed.')
        return True









    
    