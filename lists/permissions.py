from rest_framework import permissions
class IsOwnerOrPublic(permissions.BasePermission):
    """
    - SAFE methods: allowed if list is public or if owner.
    - UNSAFE methods: allowed for owner only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        return obj.user == request.user