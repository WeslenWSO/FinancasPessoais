from datetime import date
from decimal import Decimal

from django.utils import timezone

from financas.models import Despesa, Receita
from financas.utils import clamp_day, eh_recorrente, to_decimal


def ocorrencias_fixas(queryset, ym: str) -> list[dict]:
    y, m = map(int, ym.split('-'))
    result = []
    for it in queryset:
        if not eh_recorrente(it.tipo) or not it.ativa:
            continue
        dia = getattr(it, 'dia_recebimento', None) or getattr(it, 'dia_vencimento', None) or 1
        day = clamp_day(y, m, dia)
        data_ocorrencia = date(y, m, day)
        valor = it.valor if isinstance(it, Receita) else (it.valor if it.valor is not None else it.valor_fixo)
        item = {
            'id': it.pk,
            'descricao': it.descricao,
            'categoriaId': it.categoria_id,
            'tipo': it.tipo,
            'valor': valor,
            'data': data_ocorrencia.isoformat(),
            'formaPagamento': getattr(it, 'forma_pagamento', None),
            'contaId': getattr(it, 'conta_id', None),
            'cartaoId': getattr(it, 'cartao_id', None),
        }
        if it.data_inicio and data_ocorrencia < it.data_inicio:
            continue
        if it.data_fim and data_ocorrencia > it.data_fim:
            continue
        result.append(item)
    return result


def gasto_real_categoria_no_mes(user, categoria_id, ym: str) -> float:
    from financas.services.faturas import faturas_do_cartao
    from financas.models import Cartao

    total = Decimal('0')
    despesas = Despesa.objects.filter(
        user=user,
        tipo=Despesa.TIPO_VARIAVEL,
        forma_pagamento=Despesa.FORMA_CONTA,
        categoria_id=categoria_id,
        data__year=int(ym.split('-')[0]),
        data__month=int(ym.split('-')[1]),
    )
    for d in despesas:
        total += to_decimal(d.valor)

    for c in Cartao.objects.filter(user=user):
        faturas = faturas_do_cartao(user, c.pk, 72)
        fat = faturas.get(ym)
        if fat:
            for it in fat['itens']:
                if it.get('categoriaId') == categoria_id and it.get('tipo') == 'variavel':
                    total += to_decimal(it.get('valor'))
    return float(total)
