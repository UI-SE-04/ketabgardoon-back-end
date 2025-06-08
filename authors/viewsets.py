from rest_framework import viewsets, generics, status, filters
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
    list:    Returns a paginated list of authors with optional search and custom sorting
    retrieve: Returns a single author, increments view count once per visitor per day, includes rating stats
    create, update, partial_update, destroy: Standard CRUD operations
    """
    serializer_class = AuthorSerializer
    pagination_class = ItemPagination

    # Keep SearchFilter for ?search=
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'bio']
    filterset_fields = ['nationality__country_code']

    # Default ordering if no ?sort= is provided
    default_ordering = ['-created_at']

    def get_queryset(self):
        """
        Annotate with total_ratings and average_rating, then apply custom sort based on `?sort=`.
        Supported values:
          - sort=view            → view_count
          - sort=-view           → -view_count
          - sort=rating          → average_rating
          - sort=-rating         → -average_rating
          - sort=rating_count    → total_ratings
          - sort=-rating_count   → -total_ratings
        """
        qs = Author.objects.annotate(
            total_ratings=Count('book__rating', distinct=True),
            average_rating=Avg('book__rating__rating'),
        )

        sort_map = {
            'view': 'view_count',
            'rating': 'average_rating',
            'rating_count': 'total_ratings',
        }

        sort_param = self.request.GET.get('sort')
        if sort_param:
            descending = sort_param.startswith('-')
            key = sort_param.lstrip('-')
            if key in sort_map:
                field = sort_map[key]
                prefix = '' if descending else '-'
                return qs.order_by(f'{prefix}{field}')

        # Fallback to default ordering
        return qs.order_by(*self.default_ordering)

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
            mark_viewed_today(visitor_id, 'Author', author.pk)
            Author.objects.filter(pk=author.pk).update(view_count=F('view_count') + 1)
            # Refresh in-memory object to reflect updated count
            author.view_count = Author.objects.get(pk=author.pk).view_count

        serializer = self.get_serializer(author)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get(self, request):
        # Re‐use the same queryset (with sort + annotations) for the summary
        authors = self.get_queryset()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

class AuthorBooksView(generics.ListAPIView):
    serializer_class = AuthorBookSerializer
    pagination_class = ItemPagination  # Or set default in settings.py

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return BookAuthor.objects.filter(author__id=author_id).select_related('book', 'role')