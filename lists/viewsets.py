from rest_framework import viewsets

from lists.models import ListIcon

from lists.serializers import ListIconSerializer

class ListIconViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /lists/icons/ → list all available icons (id + URL)
    """
    queryset = ListIcon.objects.all()
    serializer_class = ListIconSerializer