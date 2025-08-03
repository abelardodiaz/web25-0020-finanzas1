from django import template
from django.forms import BoundField  # Importación necesaria
import locale
from datetime import datetime

register = template.Library()

@register.filter
def absolute(value):
    try:
        return abs(float(value))
    except (TypeError, ValueError):
        return value 

@register.filter(name='add_class')
def add_class(field, css_class):
    if not isinstance(field, BoundField):  # Ahora BoundField está definido
        return field

    attrs = {}
    if field.field.widget.attrs.get('class'):
        attrs['class'] = field.field.widget.attrs['class'] + ' ' + css_class
    else:
        attrs['class'] = css_class

    return field.as_widget(attrs=attrs) 

@register.filter
def short_date_es(value):
    months_es = {
        1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
    }
    return f"{value.day:02d}/{months_es[value.month]}"