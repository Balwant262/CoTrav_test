import datetime
import dateutil.parser
from django.utils.timesince import timesince
from django import template
from django.http import QueryDict

register = template.Library()


@register.filter
def datetime_format(date_string):
    try:
        if date_string:
            return dateutil.parser.parse(date_string).strftime('%d-%m-%Y | %H:%M')
        else:
            return None
    except ValueError:
        return None


@register.filter
def dateonly_format(date_string):
    try:
        if date_string:
            return dateutil.parser.parse(date_string).strftime('%d-%m-%Y')
        else:
            return None
    except ValueError:
        return None


@register.filter
def timeonly_format(date_string):
    try:
        if date_string:
            return dateutil.parser.parse(date_string).strftime('%H:%M')
        else:
            return None
    except ValueError:
        return None


@register.filter
def timediff_format(value, args):
    try:
        if value and args:
            date1 = dateutil.parser.parse(value).strftime('%d-%m-%Y %H:%M')
            date2 = dateutil.parser.parse(args).strftime('%d-%m-%Y %H:%M')
            return value.replace(timesince(date1, date2))
        else:
            return None
    except ValueError:
        return None


@register.filter
def priceonly_format(string):
    try:
        if string:
            str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            for char in str:
                string = string.replace(char, "")
            return string
        else:
            return None
    except ValueError:
        return None


@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg



@register.filter(name='substr')
def substr(value, arg):
    return value[:arg]


register.filter(datetime_format)
register.filter(dateonly_format)
register.filter(timeonly_format)
register.filter(timediff_format)
register.filter(priceonly_format)
register.filter(subtract)
register.filter(substr)