from django.utils.translation import gettext as _
from auto_info.custom import base_list, base_detail, fields_row
from cars.models import *


def brand_list(request):
    page_context = {
        'title': 'CARS',
        'section': _('Brands'),
        'element_url': 'cars:model_list'
    }
    objects = Brand.objects.all()
    return base_list(request, page_context, objects=objects, tempate_name='cars/brand_list.html')


def model_list(request, brand_id):
    obj = Brand.objects.get(pk=brand_id)
    page_context = {
        'title': 'CARS',
        'section': _('Models'),
        'brand': obj,
        'element_url': 'cars:generation_list'
    }
    objects = Model.objects.filter(brand_id=brand_id)
    return base_list(request, page_context, objects=objects, tempate_name='cars/model_list.html')


def generation_list(request, brand_id, model_id):
    obj = Model.objects.get(pk=model_id)
    page_context = {
        'title': 'CARS',
        'section': _('Generations'),
        'model': obj,
        'element_url': 'cars:modification_list'
    }
    objects = Generation.objects.filter(model_id=model_id)
    return base_list(request, page_context, objects=objects, tempate_name='cars/generation_list.html')


def modification_list(request, brand_id, model_id, generation_id):
    # brand = Brand.objects.get(pk=brand_id)
    obj = Generation.objects.get(pk=generation_id)
    page_context = {
        'title': 'CARS',
        'section': _('Modifications'),
        'generation': obj,
        'element_url': 'cars:modification_detail'
    }
    objects = Modification.objects.filter(generation_id=generation_id)
    return base_list(request, page_context, objects=objects, tempate_name='cars/modification_list.html')


def modification_detail(request, brand_id, model_id, generation_id, modification_id):
    obj = Modification.objects.get(pk=modification_id)

    data = fields_row(obj, excluded=['model', 'brand', 'generation'])
    page_context = {
        'title': 'CARS',
        'section': obj.name,
        'object': data
    }

    return base_detail(request, page_context, obj, tempate_name='cars/modification_detail.html')
