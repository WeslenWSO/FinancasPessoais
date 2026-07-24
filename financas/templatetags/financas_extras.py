from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def money(value):
    v = Decimal(value or 0)
    formatted = f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {formatted}'


@register.filter
def money_class(value):
    v = Decimal(value or 0)
    if v < 0:
        return 'neg'
    if v > 0:
        return 'pos'
    return ''
