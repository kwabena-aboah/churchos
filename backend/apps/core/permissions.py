from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.accounts.constants import Role


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.SUPER_ADMIN
        )


class IsAdminOrAbove(BasePermission):
    ADMIN_ROLES = {Role.SUPER_ADMIN, Role.ADMINISTRATOR}

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ADMIN_ROLES
        )


class IsAdminOrReadOnly(BasePermission):
    ADMIN_ROLES = {Role.SUPER_ADMIN, Role.ADMINISTRATOR}

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role in self.ADMIN_ROLES


class IsFinanceOrAbove(BasePermission):
    ALLOWED_ROLES = {Role.SUPER_ADMIN, Role.ADMINISTRATOR, Role.FINANCE_OFFICER}

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )


class IsPastorOrAbove(BasePermission):
    ALLOWED_ROLES = {Role.SUPER_ADMIN, Role.ADMINISTRATOR, Role.PASTOR}

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )
