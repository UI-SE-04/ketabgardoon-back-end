from rest_framework import permissions
class IsOwnerOrPublic(permissions.BasePermission):
    """
    - SAFE methods: allowed if the List is public or if the request user is the owner.
    - UNSAFE methods: allowed only for the owner.
    Works both for List and for BookList (nested under a List).
    """
    def has_object_permission(self, request, view, obj):
        # First, figure out which List we’re talking about.
        # If obj is a BookList, grab its .list; otherwise assume obj is the List itself.
        list_obj = getattr(obj, 'list', obj)

        # SAFE methods: allow if public OR owned by the requester
        if request.method in permissions.SAFE_METHODS:
            return bool(list_obj.is_public or list_obj.user == request.user)

        # UNSAFE methods: only the owner may proceed
        return bool(list_obj.user == request.user)