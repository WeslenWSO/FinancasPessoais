from decimal import Decimal

from django.utils import timezone

from financas.models import Cartao, Despesa, Orcamento, Receita
from financas.services.faturas import faturas_do_cartao
from financas.services.recorrencias import gasto_real_categoria_no_mes, ocorrencias_fixas
from financas.services.saldo import saldo_total_hoje
from financas.utils import add_months, month_key, to_decimal


def get_orcamento_table(user, ym: str | None = None) -> list[dict]:
    if not ym:
        ym = month_key(timezone.localdate())
    rows = []
    for o in Orcamento.objects.filter(user=user).select_related('categoria', 'categoria__pai'):
        planejado = to_decimal(o.valor_planejado)
        gasto = Decimal(str(gasto_real_categoria_no_mes(user, o.categoria_id, ym)))
        pct = min(100, float(gasto / planejado * 100)) if planejado > 0 else (100 if gasto > 0 else 0)
        rows.append({
            'orcamento': o,
            'planejado': planejado,
            'gasto': gasto,
            'pct': pct,
            'estourou': planejado > 0 and gasto > planejado,
        })
    return sorted(rows, key=lambda r: r['orcamento'].categoria.nome)


def get_previsao(user) -> list[dict]:
    saldo_acumulado = saldo_total_hoje(user)
    mes_atual = month_key(timezone.localdate())
    linhas = []

    for i in range(12):
        ym = add_months(mes_atual, i)
        receitas_fix = sum(
            to_decimal(r['valor'])
            for r in ocorrencias_fixas(Receita.objects.filter(user=user), ym)
        )
        receitas_var = sum(
            to_decimal(r.valor)
            for r in Receita.objects.filter(
                user=user,
                tipo=Receita.TIPO_VARIAVEL,
                data__year=int(ym.split('-')[0]),
                data__month=int(ym.split('-')[1]),
            )
        )

        despesas_fix = sum(
            to_decimal(d['valor'])
            for d in ocorrencias_fixas(
                Despesa.objects.filter(user=user, forma_pagamento=Despesa.FORMA_CONTA),
                ym,
            )
        )
        despesas_var_reais = sum(
            to_decimal(d.valor)
            for d in Despesa.objects.filter(
                user=user,
                tipo=Despesa.TIPO_VARIAVEL,
                forma_pagamento=Despesa.FORMA_CONTA,
                data__year=int(ym.split('-')[0]),
                data__month=int(ym.split('-')[1]),
            )
        )

        categorias_com_despesa = set(
            Despesa.objects.filter(
                user=user,
                tipo=Despesa.TIPO_VARIAVEL,
                forma_pagamento=Despesa.FORMA_CONTA,
                data__year=int(ym.split('-')[0]),
                data__month=int(ym.split('-')[1]),
            ).values_list('categoria_id', flat=True)
        )
        orcamento_restante = sum(
            to_decimal(o.valor_planejado)
            for o in Orcamento.objects.filter(user=user)
            if o.categoria_id not in categorias_com_despesa
        )
        despesas_var_projetadas = despesas_var_reais if i == 0 else (despesas_var_reais + orcamento_restante)

        faturas_cartao = Decimal('0')
        for c in Cartao.objects.filter(user=user):
            f = faturas_do_cartao(user, c.pk, 12)
            if ym in f:
                faturas_cartao += f[ym]['total']

        saldo_inicial_mes = saldo_acumulado
        saldo_mes = receitas_fix + receitas_var - despesas_fix - despesas_var_projetadas - faturas_cartao
        saldo_acumulado += saldo_mes

        linhas.append({
            'ym': ym,
            'saldo_inicial_mes': saldo_inicial_mes,
            'receitas_fix': receitas_fix,
            'receitas_var_reais': receitas_var,
            'despesas_fix': despesas_fix,
            'despesas_var_projetadas': despesas_var_projetadas,
            'faturas_cartao': faturas_cartao,
            'total_despesas': despesas_fix + despesas_var_projetadas + faturas_cartao,
            'saldo_mes': saldo_mes,
            'saldo_acumulado': saldo_acumulado,
        })

    return linhas
