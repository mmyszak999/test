from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow actions not in SAFE_METHODS
    only for admin.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_superuser
        )


class StaffOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow actions not in SAFE_METHODS
    only for staff member.
    """

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_staff
        )


class OwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow accessing own cart.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user


class CartOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.cart.user == request.user


class OwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or request.user == obj.user
        )
