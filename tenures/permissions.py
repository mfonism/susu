from rest_framework import permissions


class IsGroupAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user == obj.admin:
            return request.method in permissions.SAFE_METHODS
        return True


class IsGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.has_member(request.user)
