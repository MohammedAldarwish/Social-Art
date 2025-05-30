from rest_framework import permissions

class CanDelete(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if obj.user == request.user:
            return True
        
        if hasattr(obj, 'art_post') and obj.art_post.user == request.user:
            return True
        
        return False
