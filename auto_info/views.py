from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page


from auto_info.custom import render, base_list, page_iter

# redirect to general page
from cars.models import Modification as Car
from moto.models import Modification as Moto


def base(request):
    return redirect('general')


@cache_page(60 * 15)
def general(request):
    # Нужно добавить .distinct('generation__model__brand') - Работает только на PostgresSQL
    cars = Car.objects.order_by('-id')[:9]
    motos = Moto.objects.order_by('-id')[:9]
    context = {
        'title': _('General'),
        'section': _('General'),
        'element_url': 'cars:modification_detail',
        # 'cars': cars,
        # 'motos': motos
    }

    return render(request, 'base/general.html', context)


def search(request):
    query = None
    results = []
    if request.method == 'GET':
        query = request.GET.get('q', '')
        query = "".join(c for c in query if c.isalnum()).strip()
    if query:
        results = Car.objects.filter(
            Q(name__icontains=query) |
            Q(generation__name__icontains=query) |
            Q(generation__model__name__icontains=query) |
            Q(generation__model__brand__name__icontains=query)
        )

    context = {
        'page': {
            'title': _('Search'),
            'section': _('Results: ') + str(query),
        },
        'posts': page_iter(results, int(request.GET.get('page', 1)), 28),
        'query': query,
    }

    return render(request, 'base/search.html', context)
