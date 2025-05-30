from rest_framework.permissions import BasePermission

class IsInstructorOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.instructor == request.user