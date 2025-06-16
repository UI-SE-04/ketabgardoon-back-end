from django.db.models import Q

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

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

    def _ensure_owner(self, list_obj):
        if list_obj.user != self.request.user:
            raise PermissionDenied("Only the list owner may modify books.")

    @action(
        detail=True,
        methods=['get', 'post', 'delete'],
        url_path='books',
        serializer_class=BookListCreateSerializer,
        permission_classes=[IsAuthenticated],
    )
    def books(self, request, pk: int = None):
        """
        GET    /lists/{pk}/books/  → list all books in the list
        POST   /lists/{pk}/books/  → add a book  (JSON: {"book_id": …})
        DELETE /lists/{pk}/books/  → remove a book (JSON: {"book_id": …})
        """
        list_obj = self.get_object()

        # GET: list books
        if request.method == 'GET':
            qs = BookList.objects.filter(list=list_obj).select_related('book')
            page = self.paginate_queryset(qs)
            ser = BookInListSerializer(page, many=True)
            return self.get_paginated_response(ser.data)

        # POST & DELETE: must be owner
        self._ensure_owner(list_obj)

        book_id = request.data.get('book_id')
        if book_id is None:
            raise ValidationError({"book_id": "This field is required."})

        # POST: add a book
        if request.method == 'POST':
            serializer = self.get_serializer(data=request.data, context={'list_obj': list_obj})
            serializer.is_valid(raise_exception=True)
            try:
                entry = serializer.save()
            except Exception:
                raise ValidationError({"detail": "Book already in list."})
            out = BookInListSerializer(entry)
            return Response(out.data, status=status.HTTP_201_CREATED)

        # DELETE: remove a book
        deleted, _ = BookList.objects.filter(
            list=list_obj, book_id=book_id
        ).delete()
        if not deleted:
            raise NotFound(detail="Book not found in this list.")
        return Response(status=status.HTTP_204_NO_CONTENT)