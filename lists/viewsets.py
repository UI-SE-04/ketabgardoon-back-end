from django.db import Q

from rest_framework import viewsets, permissions

from lists.models import ListIcon, List

from lists.serializers import ListIconSerializer, ListSerializer



class IsOwnerOrPublic(permissions.BasePermission):
    """
    - SAFE methods: allowed if list is public or if owner.
    - UNSAFE methods: allowed for owner only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        return obj.user == request.user



class ListIconViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /lists/icons/ → list all available icons (id + URL)
    """
    queryset = ListIcon.objects.all()
    serializer_class = ListIconSerializer

class ListViewSet(viewsets.ModelViewSet):
    """
       /lists/            → list & create
    """

    queryset = List.objects.all().select_related('icon_id', 'user')
    serializer_class = ListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrPublic]

    def get_queryset(self):
        # show only public lists or your own
        user = self.request.user
        return List.objects.filter(Q(is_public=True) | Q(user=user))

    def perform_create(self, serializer):
        # bind new list to the logged-in user
        serializer.save(user=self.request.user)
