from rest_framework import viewsets, permissions, status, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from django.db.models import F, Avg, Count
from django.shortcuts import get_object_or_404

from .models import (
    Book, Publisher, Category, Store, Role, BookAuthor,
    BookStore, Rating,
)
from .serializers import (
    BookSerializer, PublisherSerializer, CategorySerializer,
    StoreSerializer, RoleSerializer, BookAuthorSerializer,
    BookISBN, BookISBNSerializer, BookStoreSerializer,
    RatingSerializer
)
from .utils import has_viewed_today, mark_viewed_today


class PublisherViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Publisher.objects.all().order_by('name')
    serializer_class = PublisherSerializer
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['created_at', 'updated_at']


class RoleViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Role.objects.all().order_by('title')
    serializer_class = RoleSerializer
    filterset_fields = ['title']
    search_fields = ['title']
    ordering_fields = ['title']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Category.objects.all().order_by('title')
    serializer_class = CategorySerializer
    filterset_fields = ['title']
    search_fields = ['title']
    ordering_fields = ['title']


class StoreViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Store.objects.all().order_by('name')
    serializer_class = StoreSerializer
    filterset_fields = ['name']
    search_fields = ['name', 'phone']
    ordering_fields = ['name']


class BookAuthorViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = BookAuthor.objects.all().order_by('added_at')
    serializer_class = BookAuthorSerializer
    filterset_fields = ['book__id', 'author__id', 'role__id']
    search_fields = ['book__title', 'author__name']
    ordering_fields = ['added_at']


class BookISBNViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = BookISBN.objects.all().order_by('isbn')
    serializer_class = BookISBNSerializer
    filterset_fields = ['book__title', 'isbn']
    search_fields = ['isbn']
    ordering_fields = ['isbn']


class BookStoreViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = BookStore.objects.all().order_by('store__name')
    serializer_class = BookStoreSerializer
    filterset_fields = ['book__id', 'store__id']
    search_fields = ['store__name', 'url']
    ordering_fields = ['store__name']


class ItemPagination(PageNumberPagination):
    """
    Simple pagination for BookViewSet
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookViewSet(viewsets.ModelViewSet):
    """
    list:    Returns a paginated list of books with optional search/ordering and rating stats
    retrieve: Returns a single book, increments view count once per visitor per day, includes rating stats
    create, update, partial_update, destroy: Standard CRUD operations
    """
    queryset = Book.objects.all().order_by('created_at')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ItemPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'description', 'authors__name', 'categories__title']
    ordering_fields = ['created_at', 'ratings_count', 'ratings_avg', 'view_count']
    ordering = ['-created_at']

    def get_queryset(self):
        # Annotate with rating statistics
        return (
            Book.objects
            .annotate(ratings_count=Count('rating', distinct=True))
            .annotate(ratings_avg=Avg('rating__rating'))
            .order_by(*self.ordering)
        )

    def list(self, request, *args, **kwargs):
        # Use annotated queryset and built-in pagination
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # Fetch and annotate single book
        book = (
            self.get_queryset()
            .filter(pk=kwargs['pk'])
            .first()
        )
        if not book:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Track view count per visitor per day
        if request.user.is_authenticated:
            visitor_id = f'user:{request.user.id}'
        else:
            if not request.session.session_key:
                request.session.save()
            visitor_id = f'session:{request.session.session_key}'

        if not has_viewed_today(visitor_id, book.pk):
            mark_viewed_today(visitor_id, book.pk)
            # Use F expression for atomic increment
            Book.objects.filter(pk=book.pk).update(view_count=F('view_count') + 1)
            # Refresh annotated view_count field
            book.view_count = Book.objects.get(pk=book.pk).view_count

        serializer = self.get_serializer(book)
        return Response(serializer.data)


class RatingsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /books/ratings/    GET list all ratings of the current user
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ItemPagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Rating.objects.filter(user=self.request.user)
        else:
            return Response(data={'details':'not authorized'}, status=status.HTTP_401_UNAUTHORIZED)


class MyRatingViewSet(viewsets.ViewSet):
    """
    /books/{book_id}/myrating/
      GET     retrieve this user’s rating on the book (404 if none)
      POST    create   (400 if already exists)
      PUT/PATCH  update  (404 if none)
      DELETE  delete   (404 if none)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_book(self):
        return get_object_or_404(Book, pk=self.kwargs['book_id'])

    def get_object(self):
        book = self.get_book()
        try:
            return Rating.objects.get(user=self.request.user, book=book)
        except Rating.DoesNotExist:
            raise NotFound('You have not rated this book.')

    def retrieve(self, request, book_id=None):
        rating = self.get_object()
        return Response(RatingSerializer(rating).data)

    def create(self, request, book_id=None):
        book = self.get_book()
        if Rating.objects.filter(user=request.user, book=book).exists():
            raise ValidationError('You’ve already rated this book.')
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, book=book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, book_id=None):
        rating = self.get_object()
        serializer = RatingSerializer(rating, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, book_id=None):
        rating = self.get_object()
        rating.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
