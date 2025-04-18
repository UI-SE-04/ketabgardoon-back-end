from rest_framework import viewsets
from .models import Country
from .serializers import CountrySerializer

class NationalityViewSet(viewsets.ModelViewSet):
    """
    list, retrieve, create, update, partial_update, destroy
    """
    queryset = Country.objects.all().order_by('country')
    serializer_class = CountrySerializer
    search_fields = ['country', 'country_code']
    ordering_fields = ['country']
