from django import template
import urllib.parse
register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


@register.filter(name='remove_character')
def remove_character(breadcrumb):
    return breadcrumb.replace('%20', ' ')


@register.filter(name='html_decode')
def html_decode(url):
    return urllib.parse.unquote(url)
