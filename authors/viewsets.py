from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django.db.models import Avg, Count


from .models import Author
from books.models import BookAuthor
from .serializers import AuthorSerializer
from .serializers import AuthorBookSerializer


class ItemPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100





class AuthorViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    # Always annotate authors with rating stats for list/retrieve
    queryset = Author.objects.annotate(
        total_ratings = Count('book__rating'),
        average_rating = Avg('book__rating__rating'),
    )
    serializer_class = AuthorSerializer
    pagination_class = ItemPagination
    filterset_fields = ['nationality__country_code']
    search_fields = ['name', 'bio']
    ordering_fields = ['created_at', 'rating']

    @action(detail=False, methods=['get'])
    def get(self, request):
        # Re‐use the same queryset annotations for the summary
        authors = self.get_queryset()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)


class AuthorBooksView(generics.ListAPIView):
    serializer_class = AuthorBookSerializer
    pagination_class = ItemPagination  # Or set default in settings.py

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return BookAuthor.objects.filter(author__id=author_id).select_related('book', 'role')