from django.template import Library
from django.utils.safestring import mark_safe
from HTMLParser import HTMLParser


register = Library()


@register.filter
def custom_safe(value):
    html_parser = HTMLParser()
    unescaped = html_parser.unescape(value)
    return mark_safe(unescaped)
