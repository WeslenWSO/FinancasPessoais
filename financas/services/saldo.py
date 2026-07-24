from decimal import Decimal

from django.utils import timezone

from financas.models import Cartao, Conta, Despesa, Investimento, Receita
from financas.services.faturas import faturas_do_cartao, vencimento_da_fatura
from financas.utils import add_months, clamp_day, month_key, to_decimal


def saldo_conta_ate_hoje(user, conta_id) -> Decimal:
    conta = Conta.objects.filter(user=user, pk=conta_id).first()
    if not conta:
        return Decimal('0')

    hoje = timezone.localdate().isoformat()
    saldo = to_decimal(conta.saldo_inicial)

    for r in Receita.objects.filter(user=user, conta_id=conta_id):
        if r.tipo == Receita.TIPO_VARIAVEL:
            if r.data and r.data.isoformat() <= hoje:
                saldo += to_decimal(r.valor)
        else:
            ym = r.data_inicio.strftime('%Y-%m') if r.data_inicio else month_key(timezone.localdate())
            fim = month_key(timezone.localdate())
            while ym <= fim:
                if r.ativa:
                    y, m = map(int, ym.split('-'))
                    dt = f'{ym}-{clamp_day(y, m, r.dia_recebimento or 1):02d}'
                    inicio_ok = not r.data_inicio or dt >= r.data_inicio.isoformat()
                    fim_ok = not r.data_fim or dt <= r.data_fim.isoformat()
                    if inicio_ok and fim_ok and dt <= hoje:
                        saldo += to_decimal(r.valor)
                ym = add_months(ym, 1)

    for d in Despesa.objects.filter(user=user, forma_pagamento=Despesa.FORMA_CONTA, conta_id=conta_id):
        if d.tipo == Despesa.TIPO_VARIAVEL:
            if d.data and d.data.isoformat() <= hoje:
                saldo -= to_decimal(d.valor)
        else:
            ym = d.data_inicio.strftime('%Y-%m') if d.data_inicio else month_key(timezone.localdate())
            fim = month_key(timezone.localdate())
            while ym <= fim:
                if d.ativa:
                    y, m = map(int, ym.split('-'))
                    dt = f'{ym}-{clamp_day(y, m, d.dia_vencimento or 1):02d}'
                    inicio_ok = not d.data_inicio or dt >= d.data_inicio.isoformat()
                    fim_ok = not d.data_fim or dt <= d.data_fim.isoformat()
                    if inicio_ok and fim_ok and dt <= hoje:
                        saldo -= to_decimal(d.valor_fixo)
                ym = add_months(ym, 1)

    for inv in Investimento.objects.filter(user=user, conta_id=conta_id):
        if inv.data.isoformat() > hoje:
            continue
        if inv.operacao == Investimento.OPERACAO_RESGATE:
            saldo += to_decimal(inv.valor)
        else:
            saldo -= to_decimal(inv.valor)

    for c in Cartao.objects.filter(user=user, conta_pagamento_id=conta_id):
        faturas = faturas_do_cartao(user, c.pk, 0)
        for comp, fat in faturas.items():
            venc = vencimento_da_fatura(c, comp)
            if venc <= hoje:
                saldo -= fat['total']

    return saldo


def saldo_total_hoje(user) -> Decimal:
    total = Decimal('0')
    for conta in Conta.objects.filter(user=user):
        total += saldo_conta_ate_hoje(user, conta.pk)
    return total
