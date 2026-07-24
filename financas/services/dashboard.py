from decimal import Decimal

from django.utils import timezone

from financas.models import Bem, Cartao, Categoria, Despesa, Investimento, Orcamento, Receita
from financas.services.faturas import (
    faturas_do_cartao,
    fechamento_da_fatura,
    limite_disponivel_cartao,
    status_fatura,
    vencimento_da_fatura,
)
from financas.services.recorrencias import gasto_real_categoria_no_mes, ocorrencias_fixas
from financas.services.saldo import saldo_total_hoje
from financas.utils import add_months, month_key, to_decimal


def categoria_label_completo(categoria_id, categorias):
    cat = next((c for c in categorias if c.pk == categoria_id), None)
    if not cat:
        return '—'
    if cat.pai_id:
        pai = next((c for c in categorias if c.pk == cat.pai_id), None)
        return f'{pai.nome} › {cat.nome}' if pai else cat.nome
    return cat.nome


def get_dashboard_data(user, ym: str | None = None) -> dict:
    if not ym:
        ym = month_key(timezone.localdate())

    receitas_var = Receita.objects.filter(
        user=user,
        tipo=Receita.TIPO_VARIAVEL,
        data__year=int(ym.split('-')[0]),
        data__month=int(ym.split('-')[1]),
    )
    receitas_fix = ocorrencias_fixas(Receita.objects.filter(user=user), ym)
    total_receitas = sum(to_decimal(r.valor) for r in receitas_var) + sum(
        to_decimal(r['valor']) for r in receitas_fix
    )

    despesas_var_conta = Despesa.objects.filter(
        user=user,
        tipo=Despesa.TIPO_VARIAVEL,
        forma_pagamento=Despesa.FORMA_CONTA,
        data__year=int(ym.split('-')[0]),
        data__month=int(ym.split('-')[1]),
    )
    despesas_fix_conta = ocorrencias_fixas(
        Despesa.objects.filter(user=user, forma_pagamento=Despesa.FORMA_CONTA),
        ym,
    )
    total_faturas_mes = Decimal('0')
    cartao_rows = []
    for c in Cartao.objects.filter(user=user):
        faturas = faturas_do_cartao(user, c.pk, 12)
        fat = faturas.get(ym, {'itens': [], 'total': Decimal('0')})
        total_faturas_mes += fat['total']
        cartao_rows.append({
            'cartao': c,
            'comp': ym,
            'total': fat['total'],
            'status': status_fatura(c, ym),
            'fechamento': fechamento_da_fatura(c, ym),
            'vencimento': vencimento_da_fatura(c, ym),
        })

    total_despesas = (
        sum(to_decimal(d.valor) for d in despesas_var_conta)
        + sum(to_decimal(d['valor']) for d in despesas_fix_conta)
        + total_faturas_mes
    )

    saldo_total = saldo_total_hoje(user)
    total_aportes = sum(
        to_decimal(i.valor)
        for i in Investimento.objects.filter(user=user, operacao=Investimento.OPERACAO_APORTE)
    )
    total_resgates = sum(
        to_decimal(i.valor)
        for i in Investimento.objects.filter(user=user, operacao=Investimento.OPERACAO_RESGATE)
    )
    investido_atual = total_aportes - total_resgates
    patrimonio_bens = sum(
        to_decimal(b.valor_estimado_atual)
        if b.valor_estimado_atual is not None
        else to_decimal(b.valor_aquisicao)
        for b in Bem.objects.filter(user=user)
    )

    meses = [add_months(ym, -i) for i in range(5, -1, -1)]
    serie_receita = []
    serie_despesa = []
    for m in meses:
        v1 = sum(
            to_decimal(r.valor)
            for r in Receita.objects.filter(
                user=user,
                tipo=Receita.TIPO_VARIAVEL,
                data__year=int(m.split('-')[0]),
                data__month=int(m.split('-')[1]),
            )
        )
        v2 = sum(to_decimal(r['valor']) for r in ocorrencias_fixas(Receita.objects.filter(user=user), m))
        serie_receita.append(float(v1 + v2))

        d1 = sum(
            to_decimal(d.valor)
            for d in Despesa.objects.filter(
                user=user,
                tipo=Despesa.TIPO_VARIAVEL,
                forma_pagamento=Despesa.FORMA_CONTA,
                data__year=int(m.split('-')[0]),
                data__month=int(m.split('-')[1]),
            )
        )
        d2 = sum(
            to_decimal(d['valor'])
            for d in ocorrencias_fixas(
                Despesa.objects.filter(user=user, forma_pagamento=Despesa.FORMA_CONTA),
                m,
            )
        )
        d3 = Decimal('0')
        for c in Cartao.objects.filter(user=user):
            f = faturas_do_cartao(user, c.pk, 12)
            d3 += f.get(m, {'total': Decimal('0')})['total']
        serie_despesa.append(float(d1 + d2 + d3))

    categorias_despesa = list(Categoria.objects.filter(user=user, tipo=Categoria.TIPO_DESPESA))
    por_categoria = {}
    for d in list(despesas_var_conta) + despesas_fix_conta:
        key = d.categoria_id if hasattr(d, 'categoria_id') else d.get('categoriaId')
        val = d.valor if hasattr(d, 'valor') else d.get('valor')
        por_categoria[key] = por_categoria.get(key, Decimal('0')) + to_decimal(val)
    for row in cartao_rows:
        faturas = faturas_do_cartao(user, row['cartao'].pk, 12)
        fat = faturas.get(ym)
        if fat:
            for it in fat['itens']:
                key = it.get('categoriaId')
                por_categoria[key] = por_categoria.get(key, Decimal('0')) + to_decimal(it.get('valor'))

    donut_data = sorted(
        [
            {
                'label': categoria_label_completo(k, categorias_despesa) if k else 'Sem categoria',
                'value': float(v),
                'color': next((c.cor for c in categorias_despesa if c.pk == k), '#9ca3af'),
            }
            for k, v in por_categoria.items()
        ],
        key=lambda x: x['value'],
        reverse=True,
    )

    limites = []
    cartoes_em_uso = Cartao.objects.filter(user=user, limite__gt=0).filter(
        despesas__isnull=False,
    ).distinct()
    for c in cartoes_em_uso:
        L = limite_disponivel_cartao(user, c.pk)
        pct = min(100, max(0, float(L['usado'] / L['limite'] * 100))) if L['limite'] > 0 else 0
        limites.append({'cartao': c, **L, 'pct': pct})

    orcamentos = []
    for o in Orcamento.objects.filter(user=user).select_related('categoria'):
        planejado = to_decimal(o.valor_planejado)
        gasto = Decimal(str(gasto_real_categoria_no_mes(user, o.categoria_id, ym)))
        pct = min(100, float(gasto / planejado * 100)) if planejado > 0 else (100 if gasto > 0 else 0)
        orcamentos.append({
            'orcamento': o,
            'planejado': planejado,
            'gasto': gasto,
            'pct': pct,
            'estourou': planejado > 0 and gasto > planejado,
        })

    return {
        'ym': ym,
        'saldo_total': saldo_total,
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'saldo_mes': total_receitas - total_despesas,
        'investido_atual': investido_atual,
        'patrimonio_bens': patrimonio_bens,
        'cartao_rows': cartao_rows,
        'limites': limites,
        'orcamentos': orcamentos,
        'chart_labels': meses,
        'serie_receita': serie_receita,
        'serie_despesa': serie_despesa,
        'donut_data': donut_data,
        'sparkline': [r - d for r, d in zip(serie_receita, serie_despesa)],
    }
