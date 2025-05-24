from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsSupplierUser(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'supplier'

class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user

class IsSupplierProductOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'supplier_profile')

    def has_object_permission(self, request, view, obj):
        return (
            hasattr(request.user, 'supplier_profile') and
            obj.supplier == request.user.supplier_profile
        )

