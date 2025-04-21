from rest_framework import viewsets

from .models import Author
from .serializers import AuthorSerializer

class AuthorViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    filterset_fields = ['nationality__country_code']
    search_fields = ['name', 'bio']
    ordering_fields = ['created_at', 'rating']
