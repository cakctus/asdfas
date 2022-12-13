from django.utils.translation import gettext as _
from auto_info.custom import base_list, base_detail, fields_row
from moto.models import *


def brand_list(request):
    page_context = {
        'title': 'MOTO',
        'section': _('Brands'),
        'element_url': 'moto:model_list'
    }
    objects = Brand.objects.all()
    return base_list(request, page_context, objects=objects, tempate_name='moto/brand_list.html')


def model_list(request, brand_id):
    obj = Brand.objects.get(pk=brand_id)
    page_context = {
        'title': 'MOTO',
        'section': _('Models'),
        'brand': obj,
        'element_url': 'moto:modification_list'
    }
    objects = Model.objects.filter(brand_id=brand_id)
    return base_list(request, page_context, objects=objects, tempate_name='moto/model_list.html')


def modification_list(request, brand_id, model_id):
    # brand = Brand.objects.get(pk=brand_id)
    obj = Model.objects.get(pk=model_id)
    page_context = {
        'title': 'MOTO',
        'section': _('Modifications'),
        'model': obj,
        'element_url': 'moto:modification_detail'
    }
    objects = Modification.objects.filter(model_id=model_id)
    return base_list(request, page_context, objects=objects, tempate_name='moto/modification_list.html')


def modification_detail(request, brand_id, model_id, modification_id):
    obj = Modification.objects.get(pk=modification_id)

    data = fields_row(obj, excluded=['model', 'brand'])
    page_context = {
        'title': 'MOTO',
        'section': obj.name,
        'object': data
    }

    return base_detail(request, page_context, obj, tempate_name='moto/modification_detail.html')
