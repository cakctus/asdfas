from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import BigAutoField
from django.forms import model_to_dict
from django.http import HttpResponse
from django.template import loader


def render(request, template_name, context=None, content_type=None, status=None, using=None):
    if context is None:
        context = {}
    if not context.get('page'):
        context.update({
            'page': {
                'title': 'AUTO INFO'
            }
        })

    content = loader.render_to_string(template_name, context, request, using=using)
    return HttpResponse(content, content_type, status)


def page_iter(obj_list, page, count=50):
    paginator = Paginator(obj_list, count)
    try:
        obj_list = paginator.page(page)
    except PageNotAnInteger:
        obj_list = paginator.page(1)
    except EmptyPage:
        obj_list = paginator.page(paginator.num_pages)
    return obj_list


def base_list(request, page_context, objects, tempate_name, post_count=200):
    context = {
        'page': page_context,
        'posts': page_iter(objects, int(request.GET.get('page', 1)), post_count)
    }
    return render(request, tempate_name, context)


def base_detail(request, page_context, obj, tempate_name):
    context = {
        'page': page_context,
        'post': obj
    }
    return render(request, tempate_name, context)


def fields_row(obj, verbose_name=None, excluded=[]):
    data = {}
    dict_object = obj._meta.get_fields()
    model_name = verbose_name if verbose_name else obj._meta.verbose_name.capitalize()
    fields = []
    for v in dict_object:
        name = v.name
        if str(name).strip().lower() in excluded:
            print(name, 'alo lo ')
            continue
        if hasattr(obj, name):
            if name == 'id':
                continue
            value = getattr(obj, name)

            label = getattr(v, 'verbose_name').capitalize()
            if v.related_model:
                if value:
                    if 'ManyRelatedManager' in str(type(value)):
                        for val in value.all():
                            related_obj = fields_row(val, label, excluded)
                            if related_obj.get(label):
                                data.update(related_obj)
                        continue
                    related_obj = fields_row(value, label, excluded)
                    # set related data
                    if related_obj.get(label):
                        data.update(related_obj)
                continue
            if value:
                if hasattr(value, 'url'):
                    # value = getattr(value, 'url')
                    continue
                fields.append({label: value})
    data[model_name] = fields

    items = list(data.items())
    reversed_data = {k: v for k, v in reversed(items)}
    return reversed_data
