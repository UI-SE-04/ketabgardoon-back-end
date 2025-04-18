from rest_framework import viewsets
from .models import Nationality
from .serializers import NationalitySerializer

class NationalityViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Nationality.objects.all().order_by('country')
    serializer_class = NationalitySerializer
    search_fields = ['country', 'country_code']
    ordering_fields = ['country']
