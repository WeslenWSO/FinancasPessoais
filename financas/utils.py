from datetime import date, datetime
from decimal import Decimal


def month_key(d: date | datetime) -> str:
    if isinstance(d, datetime):
        d = d.date()
    return f'{d.year}-{d.month:02d}'


def add_months(ym: str, n: int) -> str:
    y, m = map(int, ym.split('-'))
    m += n
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    return f'{y}-{m:02d}'


def days_in_month(y: int, m: int) -> int:
    if m == 12:
        return (date(y + 1, 1, 1) - date(y, 12, 1)).days + 1
    return (date(y, m + 1, 1) - date(y, m, 1)).days


def clamp_day(y: int, m: int, day: int) -> int:
    return min(day, days_in_month(y, m))


def fmt_money(value) -> str:
    v = Decimal(value or 0)
    formatted = f'{v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {formatted}'


def fmt_date(d) -> str:
    if not d:
        return '—'
    if isinstance(d, str):
        y, m, day = d.split('-')
        return f'{day}/{m}/{y}'
    return d.strftime('%d/%m/%Y')


def eh_recorrente(tipo: str) -> bool:
    return tipo in ('fixa', 'consorcio')


def to_decimal(value) -> Decimal:
    if value is None or value == '':
        return Decimal('0')
    return Decimal(str(value))
