from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Book, Publisher, Category, Store, Role, BookAuthor, BookStore
from .serializers import BookSerializer, PublisherSerializer, CategorySerializer, StoreSerializer, RoleSerializer, \
    BookAuthorSerializer, BookISBN, BookISBNSerializer, BookStoreSerializer
from .utils import has_viewed_today, mark_viewed_today
from django.db.models import F


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
    queryset = Book.objects.all().order_by('created_at')
    serializer_class = BookSerializer
    filterset_fields = ['publisher__id', 'published_date']
    search_fields = ['title', 'published_date','category__title']
    ordering_fields = ['published_date']
    permission_classes = [permissions.AllowAny]

    def retrieve(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs['pk'])
        book_id = book.pk

        if request.user.is_authenticated:
            visitor_id = f'user:{request.user.id}'
        else:
            if not request.session.session_key:
                request.session.save()
            visitor_id = f'session:{request.session.session_key}'

        if not has_viewed_today(visitor_id, book_id):
            mark_viewed_today(visitor_id, book_id)
            Book.objects.filter(pk=book_id).update(view_count=F('view_count') + 1)
            book.refresh_from_db(fields=["view_count"])
        serializer = self.get_serializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)