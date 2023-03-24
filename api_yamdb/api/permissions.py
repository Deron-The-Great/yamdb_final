from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class AdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            (request.user.is_authenticated and request.user.is_admin)
            or (request.method in SAFE_METHODS)
        )


class IsAdminModeratorAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.user.is_authenticated and (
                request.user.is_admin or request.user.is_moderator
            ) or request.method in SAFE_METHODS
        )
