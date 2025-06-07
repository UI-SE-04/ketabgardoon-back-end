from django.db.models import Q

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from lists.models import List, BookList
from lists.permissions import IsOwnerOrPublic
from lists.serializers import ListSerializer, BookInListSerializer, BookListCreateSerializer
from lists.filters import ListFilter


class ListViewSet(viewsets.ModelViewSet):
    """
    /lists/       → list & create
    /lists/{pk}/  → retrieve, update, destroy
    /lists/{pk}/books/ → list, add, remove books
    """

    queryset = List.objects.all().select_related('user')
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrPublic]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ListFilter
    search_fields = ['name', 'description']

    def get_queryset(self):
        """
        Anonymous users: only public lists.
        Authenticated users: public lists + their own.
        Then apply any filter parameters.
        """
        base_qs = List.objects.all().select_related('user')
        user = self.request.user

        if not user.is_authenticated:
            base_qs = base_qs.filter(is_public=True)
        else:
            # include both public and own, unless "mine" was specified which overrides
            base_qs = base_qs.filter(Q(is_public=True) | Q(user=user))

        return base_qs

    def perform_create(self, serializer):
        # Bind new list to the logged‐in user.
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=['get', 'post', 'delete'],
        url_path='books',
        permission_classes=[IsAuthenticatedOrReadOnly, IsOwnerOrPublic],
    )
    def books(self, request, pk=None):
        """
        GET    /lists/{pk}/books/   → list books (public or owner)
        POST   /lists/{pk}/books/   → add a book (owner only)
        DELETE /lists/{pk}/books/?book_id=… → remove a book (owner only)
        """
        list_obj = self.get_object()

        # LIST BOOKS
        if request.method == 'GET':
            paginator = PageNumberPagination()
            paginator.page_size = 8
            entries = (
                BookList.objects
                .filter(list=list_obj)
                .select_related('book')
            )
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
            except Exception:
                return Response(
                    {'detail': 'Book already in list.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            out = BookInListSerializer(entry)
            return Response(out.data, status=status.HTTP_201_CREATED)

        # REMOVE A BOOK
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