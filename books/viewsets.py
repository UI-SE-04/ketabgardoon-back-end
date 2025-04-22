from rest_framework import viewsets
from .models import Book, Publisher, Category, Store,Role
from .serializers import BookSerializer, PublisherSerializer, CategorySerializer, StoreSerializer,RoleSerializer

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