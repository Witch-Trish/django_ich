from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import SubTask, Task

class IsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return True
        if isinstance(obj, SubTask):
            owner = getattr(obj, 'owner', None) or getattr(obj.task, 'owner', None)
        else:
            owner = getattr(obj, 'owner', None)
        if owner is not None:
            return owner == request.user
        return False