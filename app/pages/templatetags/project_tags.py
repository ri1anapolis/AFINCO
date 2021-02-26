from django import template
from django.conf import settings
from django.utils.formats import number_format

from datetime import date, datetime, timedelta
import re
from decimal import Decimal

register = template.Library()

@register.simple_tag
def project_version():
    if settings.PROJECT_VERSION:
        return str(settings.PROJECT_VERSION)
    return ''

@register.simple_tag
def project_env():
    if settings.PROJECT_ENV:
        return str(settings.PROJECT_ENV)
    return ''

@register.simple_tag
def url_replace(request, field, value):
    d = request.GET.copy()
    d[field] = value
    return d.urlencode()

@register.simple_tag
def url_delete(request, field):
    d = request.GET.copy()
    del d[field]
    return d.urlencode()

@register.simple_tag
def addDaysToDate(_date, _days):
    """Sum some days to given date or show
        tomorrow's date if nothing valid is given"""
    if not isinstance(_date, date):
        _date=date.today()
    if not isinstance(_days, int):
        _days = 1
    _new_date = _date + timedelta(days=_days)
    return _new_date.strftime('%Y-%m-%d')

@register.filter(is_safe=True)
def intseparator(value, use_l10n=True):
    """
    ::: A copy from django.contrib.humanize's intseparator filter.
    ::: The filter uses dots (.) instead of commas (,).
    Convert an integer to a string containing dots every three digits.
    For example, 3000 becomes '3.000' and 45000 becomes '45.000'.
    """
    _DEFAULT_SEPARATOR = ','

    if settings.THOUSAND_SEPARATOR:
        _DEFAULT_SEPARATOR = settings.THOUSAND_SEPARATOR

    if settings.USE_L10N and use_l10n:
        try:
            if not isinstance(value, (float, Decimal)):
                value = int(value)
        except (TypeError, ValueError):
            return intseparator(value, False)
        else:
            return number_format(value, force_grouping=True)
    orig = str(value)
    new = re.sub(r"^(-?\d+)(\d{3})", r'\g<1>' + _DEFAULT_SEPARATOR + r'\g<2>', orig)
    if orig == new:
        return new
    else:
        return intseparator(new, use_l10n)

def only_digits(value):
    only_digits = re.compile(r'[^\d]+')
    return only_digits.sub('', str(value))

@register.filter(is_safe=True)
def cpf(cpf):
    if cpf:
        cpf = only_digits(cpf)

        if len(cpf) == 11:
            return f'{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}'

    return None

@register.filter(is_safe=True)
def cnpj(cnpj):
    if cnpj:
        cnpj = only_digits(cnpj)

        if len(cnpj) == 14:
            return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'

    return None

@register.filter(is_safe=True)
def phone(phone):
    if phone:
        if len(str(phone)) < 8:  # retorna sem formatação
            return phone

        phone = only_digits(phone)

        if len(phone) == 8:
            return f'{phone[:4]}-{phone[4:]}'
        elif len(phone) == 9:
            return f'{phone[0]} {phone[1:5]}-{phone[5:]}'
        elif len(phone) == 10:
            return f'({phone[:2]}) {phone[2:6]}-{phone[6:]}'
        elif len(phone) == 11:
            return f'({phone[:2]}) {phone[2]} {phone[3:7]}-{phone[7:]}'
        elif len(phone) == 12:
            return f'+{phone[:2]} ({phone[2:4]}) {phone[4:8]}-{phone[8:]}'
        elif len(phone) == 13:
            return f'+{phone[:2]} ({phone[2:4]}) {phone[4]} {phone[5:9]}-{phone[9:]}'

    return None