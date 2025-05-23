from django.db import Q

from rest_framework import viewsets, permissions
from rest_framework.decorators import action

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
    /lists/{pk}/       → retrieve, update, destroy
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

    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_pk>\d+)')
    def user_lists(self, request, user_pk=None):
        """
        GET /lists/user/{user_pk}/
        → if you’re the same user: all your lists
        → otherwise: only that user’s public lists
        """
        qs = List.objects.filter(user__pk=user_pk)
        if request.user.pk != int(user_pk):
            qs = qs.filter(is_public=True)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
