from django import template

register = template.Library()



@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, False)  # add fallback default

@register.filter
def split(value, arg):
    return value.split(arg)[-1]

@register.filter
def replace(value, arg):
    old, new = arg.split(',')
    return value.replace(old, new)

@register.filter
def replace_underscores(value):
    return value.replace('_', ' ').title()