from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Author
from .serializers import AuthorSerializer

class AuthorViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    + custom actions: recalc (per-instance) & recalc_all
    """
    queryset = Author.objects.all().order_by('name')
    serializer_class = AuthorSerializer
    filterset_fields = ['nationality__country_code']
    search_fields = ['name', 'bio']
    ordering_fields = ['created_at', 'rating']

    @action(detail=True, methods=['post'])
    def recalc(self, request, pk=None):
        """
        POST /api/v1/authors/{pk}/recalc/
        """
        author = self.get_object()
        if not author.total_number_of_ratings:
            return Response(
                {'detail': 'no ratings to recalc'},
                status=status.HTTP_400_BAD_REQUEST
            )
        author.update_rating()
        return Response({'rating': author.rating})

    @action(detail=False, methods=['post'])
    def recalc_all(self, request):
        """
        POST /api/v1/authors/recalc_all/
        """
        updated = 0
        for author in Author.objects.exclude(total_number_of_ratings__in=[0, None]):
            author.update_rating()
            updated += 1
        return Response({'updated_authors': updated})