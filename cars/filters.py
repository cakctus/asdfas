import django_filters

from .models import Modification


class ModificationFilter(django_filters.FilterSet):

    class Meta:
        model = Modification
        fields = ['generation']