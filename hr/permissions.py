from rest_framework import permissions


class IsNotRussianEmail(permissions.BasePermission):
    """
    Allows access only to users whose email does not end with .ru
    """

    def has_permission(self, request, view):
        if request.user and request.user.email:
            return not request.user.email.endswith('.ru')
        return False


class HasPositionPermission(permissions.BasePermission):
    """
    Allows access only to employees who have a position assigned.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        try:
            return user.employee.position is not None
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        return obj.position is not None
