from django.db.models import Q

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from lists.models import List, BookList

from lists.serializers import ListSerializer, BookInListSerializer, BookListCreateSerializer


class IsOwnerOrPublic(permissions.BasePermission):
    """
    - SAFE methods: allowed if list is public or if owner.
    - UNSAFE methods: allowed for owner only.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.is_public or obj.user == request.user
        return obj.user == request.user


class ListViewSet(viewsets.ModelViewSet):
    """
    /lists/            → list & create
    /lists/{pk}/       → retrieve, update, destroy
    /lists/{pk}/books/ → list, add, remove books
    /lists/user/{id}/  → lists of a given user
    """

    queryset = List.objects.all().select_related('icon_id', 'user')
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrPublic]

    def get_queryset(self):
        """
        - Anonymous users: only public lists.
        - Authenticated users: public lists plus their own.
        """
        user = self.request.user
        if user.is_authenticated:
            return List.objects.filter(Q(is_public=True) | Q(user=user))
        return List.objects.filter(is_public=True)

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

    @action(detail=True, methods=['get', 'post', 'delete'], url_path='books')
    def books(self, request, pk=None):
        """
        GET  /lists/{pk}/books/   → list books (public or owner)
        POST /lists/{pk}/books/   → add a book (owner only)
        DELETE /lists/{pk}/books/ → remove a book (owner only),
                                     passing ?book_id=…
        """
        list_obj = self.get_object()
        # LIST BOOKS
        if request.method == 'GET':
            # pagination with 8 items per page
            paginator = PageNumberPagination()
            paginator.page_size = 8
            entries = BookList.objects.filter(list=list_obj).select_related('book')
            page = paginator.paginate_queryset(entries, request)
            serializer = BookInListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # WRITE OPS: require ownership
        if list_obj.user != request.user:
            return Response({'detail': 'Forbidden.'},
                            status=status.HTTP_403_FORBIDDEN)

        # ADD A BOOK
        if request.method == 'POST':
            ser = BookListCreateSerializer(
                data=request.data,
                context={'list_obj': list_obj}
            )
            ser.is_valid(raise_exception=True)
            try:
                entry = ser.save()
            except Exception as e:
                return Response(
                    {'detail': 'Book already in list.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            out = BookInListSerializer(entry)
            return Response(out.data, status=status.HTTP_201_CREATED)

        # REMOVE A BOOK
        if request.method == 'DELETE':
            book_id = request.query_params.get('book_id')
            if not book_id:
                return Response(
                    {'detail': 'book_id query parameter required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            deleted, _ = BookList.objects.filter(
                list=list_obj, book_id=book_id
            ).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Book not found in this list.'},
                status=status.HTTP_404_NOT_FOUND
            )