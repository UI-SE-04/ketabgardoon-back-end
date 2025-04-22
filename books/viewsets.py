from rest_framework import viewsets
from .models import Book, Publisher, Category, Store, Role, BookAuthor, BookStore
from .serializers import BookSerializer, PublisherSerializer, CategorySerializer, StoreSerializer, RoleSerializer, \
    BookAuthorSerializer, BookISBN, BookISBNSerializer, BookStoreSerializer


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
class BookViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Book.objects.all().order_by('published_date')
    serializer_class = BookSerializer
    filterset_fields = ['publisher__id', 'published_date']
    search_fields = ['title', 'published_date','category__title']
    ordering_fields = ['created_at', 'updated_at', 'published_date']