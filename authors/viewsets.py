from rest_framework import viewsets
from rest_framework import generics

from .models import Author
from books.models import BookAuthor

from .serializers import AuthorSerializer
from .serializers import AuthorBookSerializer

from rest_framework.pagination import PageNumberPagination


class AuthorViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    filterset_fields = ['nationality__country_code']
    search_fields = ['name', 'bio']
    ordering_fields = ['created_at', 'rating']


class AuthorBooksView(generics.ListAPIView):
    class EightItemPagination(PageNumberPagination):
        page_size = 8
        page_size_query_param = 'page_size'
        max_page_size = 8
    serializer_class = AuthorBookSerializer
    pagination_class = EightItemPagination  # Or set default in settings.py

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return BookAuthor.objects.filter(author__id=author_id).select_related('book', 'role')