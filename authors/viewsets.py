from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Author
from .serializers import AuthorSerializer

from books.models import BookAuthor
from books.serializers import BookIdListSerializer



class AuthorViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    filterset_fields = ['nationality__country_code']
    search_fields = ['name', 'bio']
    ordering_fields = ['created_at', 'rating']


class AuthorBooksView(APIView):
    def get(self, request, author_id):
        try:
            book_ids = BookAuthor.objects.filter(author__id=author_id).values_list('book__id', flat=True)
            serializer = BookIdListSerializer({"book_ids": list(book_ids)})
            return Response(serializer.data)
        except Author.DoesNotExist:
            return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)


