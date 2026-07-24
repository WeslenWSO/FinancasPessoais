from datetime import date
from decimal import Decimal

from django.utils import timezone

from financas.models import Cartao, Despesa
from financas.utils import add_months, clamp_day, days_in_month, eh_recorrente, month_key, to_decimal


def _cartao_dict(cartao: Cartao) -> dict:
    return {
        'id': cartao.pk,
        'nome': cartao.nome,
        'contaPagamentoId': cartao.conta_pagamento_id,
        'limite': cartao.limite,
        'diaFechamento': cartao.dia_fechamento,
        'diaVencimento': cartao.dia_vencimento,
    }


def _despesa_dict(d: Despesa, valor_override=None) -> dict:
    return {
        'id': d.pk,
        'descricao': d.descricao,
        'categoriaId': d.categoria_id,
        'formaPagamento': d.forma_pagamento,
        'contaId': d.conta_id,
        'cartaoId': d.cartao_id,
        'tipo': d.tipo,
        'valor': valor_override if valor_override is not None else d.valor,
        'valorFixo': d.valor_fixo,
        'data': d.data.isoformat() if d.data else None,
        'diaVencimento': d.dia_vencimento,
        'dataInicio': d.data_inicio.isoformat() if d.data_inicio else None,
        'dataFim': d.data_fim.isoformat() if d.data_fim else None,
        'ativa': d.ativa,
        'parcelaAtual': d.parcela_atual,
        'parcelaTotal': d.parcela_total,
    }


def competencia_base(cartao: Cartao | dict, data_str: str | date | None) -> str:
    if isinstance(cartao, Cartao):
        cartao = _cartao_dict(cartao)
    if data_str:
        if isinstance(data_str, date):
            d = data_str
        else:
            d = date.fromisoformat(data_str)
    else:
        d = timezone.localdate()
    y, m = d.year, d.month
    if d.day > cartao['diaFechamento']:
        m += 1
        if m > 12:
            m = 1
            y += 1
    return f'{y}-{m:02d}'


def competencia_despesa(cartao: Cartao | dict, despesa: Despesa | dict) -> str:
    if isinstance(despesa, Despesa):
        data = despesa.data.isoformat() if despesa.data else None
        parcela_atual = despesa.parcela_atual or 1
    else:
        data = despesa.get('data')
        parcela_atual = despesa.get('parcelaAtual') or 1
    base = competencia_base(cartao, data)
    return add_months(base, parcela_atual - 1)


def vencimento_da_fatura(cartao: Cartao | dict, competencia: str) -> str:
    if isinstance(cartao, Cartao):
        cartao = _cartao_dict(cartao)
    y, m = map(int, competencia.split('-'))
    if cartao['diaVencimento'] <= cartao['diaFechamento']:
        m += 1
        if m > 12:
            m = 1
            y += 1
    day = clamp_day(y, m, cartao['diaVencimento'])
    return f'{y}-{m:02d}-{day:02d}'


def fechamento_da_fatura(cartao: Cartao | dict, competencia: str) -> str:
    if isinstance(cartao, Cartao):
        cartao = _cartao_dict(cartao)
    y, m = map(int, competencia.split('-'))
    day = clamp_day(y, m, cartao['diaFechamento'])
    return f'{y}-{m:02d}-{day:02d}'


def status_fatura(cartao: Cartao | dict, competencia: str) -> str:
    hoje = timezone.localdate().isoformat()
    fech = fechamento_da_fatura(cartao, competencia)
    venc = vencimento_da_fatura(cartao, competencia)
    if hoje > venc:
        return 'paga'
    if hoje > fech:
        return 'fechada'
    return 'aberta'


def faturas_do_cartao(user, cartao_id, meses_futuros=12) -> dict:
    cartao = Cartao.objects.filter(user=user, pk=cartao_id).first()
    out = {}
    if not cartao:
        return out

    despesas_var = Despesa.objects.filter(
        user=user,
        forma_pagamento=Despesa.FORMA_CARTAO,
        cartao_id=cartao_id,
        tipo=Despesa.TIPO_VARIAVEL,
    )
    for d in despesas_var:
        comp = competencia_despesa(cartao, d)
        out.setdefault(comp, {'itens': [], 'total': Decimal('0')})
        out[comp]['itens'].append(_despesa_dict(d))
        out[comp]['total'] += to_decimal(d.valor)

    fixas = Despesa.objects.filter(
        user=user,
        forma_pagamento=Despesa.FORMA_CARTAO,
        cartao_id=cartao_id,
        tipo__in=[Despesa.TIPO_FIXA, Despesa.TIPO_CONSORCIO],
        ativa=True,
    )
    hoje = timezone.localdate()
    limite = meses_futuros or 12
    for i in range(-1, limite + 1):
        comp = add_months(month_key(hoje), i)
        cy, cm = map(int, comp.split('-'))
        for d in fixas:
            dia = d.dia_vencimento or 1
            data_ocorrencia = f'{comp}-{clamp_day(cy, cm, dia):02d}'
            if d.data_inicio and data_ocorrencia < d.data_inicio.isoformat():
                continue
            if d.data_fim and data_ocorrencia > d.data_fim.isoformat():
                continue
            out.setdefault(comp, {'itens': [], 'total': Decimal('0')})
            item = _despesa_dict(d, valor_override=d.valor_fixo)
            item['data'] = data_ocorrencia
            out[comp]['itens'].append(item)
            out[comp]['total'] += to_decimal(d.valor_fixo)

    return out


def limite_disponivel_cartao(user, cartao_id) -> dict:
    cartao = Cartao.objects.filter(user=user, pk=cartao_id).first()
    if not cartao:
        return {'limite': Decimal('0'), 'usado': Decimal('0'), 'disponivel': Decimal('0')}

    hoje = timezone.localdate().isoformat()
    usado_parcelas = Decimal('0')
    for d in Despesa.objects.filter(
        user=user,
        forma_pagamento=Despesa.FORMA_CARTAO,
        cartao_id=cartao_id,
        tipo=Despesa.TIPO_VARIAVEL,
    ):
        comp = competencia_despesa(cartao, d)
        venc = vencimento_da_fatura(cartao, comp)
        if venc >= hoje:
            usado_parcelas += to_decimal(d.valor)

    comp_atual = competencia_base(cartao, hoje)
    usado_fixas = Decimal('0')
    for d in Despesa.objects.filter(
        user=user,
        forma_pagamento=Despesa.FORMA_CARTAO,
        cartao_id=cartao_id,
        tipo__in=[Despesa.TIPO_FIXA, Despesa.TIPO_CONSORCIO],
        ativa=True,
    ):
        if d.data_inicio and comp_atual < d.data_inicio.strftime('%Y-%m'):
            continue
        if d.data_fim and comp_atual > d.data_fim.strftime('%Y-%m'):
            continue
        usado_fixas += to_decimal(d.valor_fixo)

    usado = usado_parcelas + usado_fixas
    limite = to_decimal(cartao.limite)
    return {'limite': limite, 'usado': usado, 'disponivel': limite - usado}
