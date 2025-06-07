import django_filters

from lists.models import List

class ListFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user__id')
    username = django_filters.CharFilter(field_name='user__username')
    mine = django_filters.BooleanFilter(method='filter_mine')

    class Meta:
        model = List
        fields = ['user', 'username', 'mine', 'is_public']

    def filter_mine(self, queryset, name, value):
        """
        When ?mine=true (or 1), return only the authenticated user’s lists.
        """
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return queryset.none()
        return queryset.filter(user=user)
