from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django.db.models import Avg, Count, F


from .models import Author
from books.models import BookAuthor
from .serializers import AuthorSerializer
from .serializers import AuthorBookSerializer
from utils.view_cache import mark_viewed_today, has_viewed_today


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

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single author instance. Increment view count per unique visitor per day.
        """
        # Fetch the annotated author object
        author = self.get_queryset().filter(pk=kwargs['pk']).first()
        if not author:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Determine unique visitor identifier
        if request.user.is_authenticated:
            visitor_id = f'user:{request.user.id}'
        else:
            if not request.session.session_key:
                request.session.save()
            visitor_id = f'session:{request.session.session_key}'

        # Increment view_count only once per day per visitor
        if not has_viewed_today(visitor_id, 'Author', author.pk):
            mark_viewed_today(visitor_id, 'Author' ,author.pk)
            Author.objects.filter(pk=author.pk).update(view_count=F('view_count') + 1)
            # Refresh in-memory object to reflect updated count
            author.view_count = Author.objects.get(pk=author.pk).view_count

        serializer = self.get_serializer(author)
        return Response(serializer.data)


class AuthorBooksView(generics.ListAPIView):
    serializer_class = AuthorBookSerializer
    pagination_class = ItemPagination  # Or set default in settings.py

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return BookAuthor.objects.filter(author__id=author_id).select_related('book', 'role')