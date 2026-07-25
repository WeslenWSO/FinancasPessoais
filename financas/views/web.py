import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from financas.forms import (
    BemForm,
    CartaoForm,
    CategoriaForm,
    ContaForm,
    DespesaForm,
    InvestimentoForm,
    OrcamentoForm,
    ReceitaForm,
    save_with_user,
)
from financas.models import (
    Bem,
    Cartao,
    Categoria,
    Conta,
    Despesa,
    Investimento,
    Orcamento,
    Receita,
)
from financas.services.backup import export_backup_json, import_backup
from financas.services.dashboard import get_dashboard_data
from financas.services.faturas import faturas_do_cartao
from financas.services.previsao import get_orcamento_table, get_previsao
from financas.services.recorrencias import ocorrencias_fixas
from financas.services.saldo import saldo_conta_ate_hoje, saldo_total_hoje
from financas.utils import add_months, fmt_date, fmt_money, month_key
from financas.views.auth_views import criar_despesa_parcelada, criar_lancamento_repetido
from django.utils import timezone


def htmx_redirect(request, url_name, **kwargs):
    response = HttpResponse(status=204)
    response['HX-Redirect'] = reverse(url_name, kwargs=kwargs)
    response['HX-Trigger'] = 'showToast'
    return response


def toast_response(request, message, redirect_url=None):
    if request.htmx:
        if redirect_url:
            response = HttpResponse(status=204)
            response['HX-Redirect'] = redirect_url
        else:
            response = HttpResponse(status=204)
        response['HX-Trigger'] = '{"showToast": "' + message + '"}'
        return response
    messages.success(request, message)
    return redirect(redirect_url or 'dashboard')


@login_required
def dashboard(request):
    ym = request.GET.get('mes') or month_key(timezone.localdate())
    data = get_dashboard_data(request.user, ym)
    context = {
        'data': data,
        'ym': ym,
        'chart_labels_json': json.dumps(data['chart_labels']),
        'serie_receita_json': json.dumps(data['serie_receita']),
        'serie_despesa_json': json.dumps(data['serie_despesa']),
        'donut_data_json': json.dumps(data['donut_data']),
    }
    return render(request, 'financas/dashboard.html', context)


@login_required
def contas_list(request):
    contas = Conta.objects.filter(user=request.user)
    rows = [{'conta': c, 'saldo': saldo_conta_ate_hoje(request.user, c.pk)} for c in contas]
    return render(request, 'financas/contas/list.html', {'rows': rows})


@login_required
def cartoes_list(request):
    cartoes = Cartao.objects.filter(user=request.user).select_related('conta_pagamento')
    return render(request, 'financas/cartoes/list.html', {'cartoes': cartoes})


@login_required
def categorias_list(request):
    tab = request.GET.get('tab', 'receita')
    tipo = Categoria.TIPO_RECEITA if tab == 'receita' else Categoria.TIPO_DESPESA
    categorias = Categoria.objects.filter(user=request.user, tipo=tipo).select_related('pai').prefetch_related('subcategorias')
    pais = [c for c in categorias if not c.pai_id]
    return render(request, 'financas/categorias/list.html', {
        'tab': tab,
        'pais': pais,
        'categorias': categorias,
    })


@login_required
def receitas_list(request):
    ym = request.GET.get('mes') or month_key(timezone.localdate())
    todos = request.GET.get('todos') == '1'
    qs = Receita.objects.filter(user=request.user).select_related('categoria', 'conta')
    if not todos:
        fixas = ocorrencias_fixas(qs, ym)
        variaveis = qs.filter(tipo=Receita.TIPO_VARIAVEL, data__year=int(ym[:4]), data__month=int(ym[5:7]))
        return render(request, 'financas/receitas/list.html', {
            'ym': ym, 'todos': todos, 'fixas': fixas, 'variaveis': variaveis,
        })
    return render(request, 'financas/receitas/list.html', {'ym': ym, 'todos': todos, 'items': qs})


@login_required
def despesas_list(request):
    ym = request.GET.get('mes') or month_key(timezone.localdate())
    todos = request.GET.get('todos') == '1'
    qs = Despesa.objects.filter(user=request.user).select_related('categoria', 'conta', 'cartao')
    fixas = ocorrencias_fixas(qs.filter(forma_pagamento=Despesa.FORMA_CONTA), ym) if not todos else []
    variaveis_conta = qs.filter(
        tipo=Despesa.TIPO_VARIAVEL,
        forma_pagamento=Despesa.FORMA_CONTA,
        data__year=int(ym[:4]),
        data__month=int(ym[5:7]),
    ) if not todos else qs.filter(forma_pagamento=Despesa.FORMA_CONTA, tipo=Despesa.TIPO_VARIAVEL)
    fatura_groups = []
    if not todos:
        for c in Cartao.objects.filter(user=request.user):
            faturas = faturas_do_cartao(request.user, c.pk, 12)
            fat = faturas.get(ym, {'itens': [], 'total': Decimal('0')})
            if fat['itens']:
                fatura_groups.append({'cartao': c, 'itens': fat['itens'], 'total': fat['total']})
    total_fix = sum(Decimal(str(d.get('valor', 0))) for d in fixas)
    total_var = sum(Decimal(str(d.valor or 0)) for d in variaveis_conta)
    total_fat = sum(g['total'] for g in fatura_groups)
    return render(request, 'financas/despesas/list.html', {
        'ym': ym, 'todos': todos, 'fixas': fixas, 'variaveis_conta': variaveis_conta,
        'fatura_groups': fatura_groups,
        'kpis': {'fixas': total_fix, 'variaveis': total_var, 'faturas': total_fat, 'total': total_fix + total_var + total_fat},
    })


@login_required
def investimentos_list(request):
    items = Investimento.objects.filter(user=request.user).select_related('conta')
    aportes = sum(i.valor for i in items if i.operacao == Investimento.OPERACAO_APORTE)
    resgates = sum(i.valor for i in items if i.operacao == Investimento.OPERACAO_RESGATE)
    return render(request, 'financas/investimentos/list.html', {
        'items': items,
        'kpis': {'aportes': aportes, 'resgates': resgates, 'posicao': aportes - resgates},
    })


@login_required
def bens_list(request):
    bens = Bem.objects.filter(user=request.user)
    total_aquisicao = sum(b.valor_aquisicao for b in bens)
    total_estimado = sum(
        b.valor_estimado_atual if b.valor_estimado_atual is not None else b.valor_aquisicao
        for b in bens
    )
    return render(request, 'financas/bens/list.html', {
        'bens': bens,
        'kpis': {
            'quantidade': bens.count(),
            'aquisicao': total_aquisicao,
            'estimado': total_estimado,
            'valorizacao': total_estimado - total_aquisicao,
        },
    })


@login_required
def faturas_view(request):
    ym = request.GET.get('mes') or month_key(timezone.localdate())
    cartao_id = request.GET.get('cartao')
    cartoes = Cartao.objects.filter(user=request.user)
    if not cartao_id and cartoes.exists():
        cartao_id = str(cartoes.first().pk)
    cartao = cartoes.filter(pk=cartao_id).first() if cartao_id else None
    fat = {'itens': [], 'total': Decimal('0')}
    if cartao:
        faturas = faturas_do_cartao(request.user, cartao.pk, 12)
        fat = faturas.get(ym, fat)
    return render(request, 'financas/faturas/list.html', {
        'ym': ym, 'cartoes': cartoes, 'cartao': cartao, 'cartao_id': cartao_id, 'fatura': fat,
    })


@login_required
def previsao_view(request):
    ym = request.GET.get('mes') or month_key(timezone.localdate())
    orcamentos = get_orcamento_table(request.user, ym)
    linhas = get_previsao(request.user)
    return render(request, 'financas/previsao/list.html', {
        'ym': ym, 'orcamentos': orcamentos, 'linhas': linhas,
    })


@login_required
def backup_view(request):
    return render(request, 'financas/backup.html')


@login_required
def backup_export(request):
    content = export_backup_json(request.user)
    response = HttpResponse(content, content_type='application/json')
    stamp = timezone.now().strftime('%Y-%m-%d-%H-%M-%S')
    response['Content-Disposition'] = f'attachment; filename="backup-financas-{stamp}.json"'
    return response


@login_required
@require_POST
def backup_import(request):
    file = request.FILES.get('file')
    if not file:
        messages.error(request, 'Nenhum arquivo selecionado.')
        return redirect('backup')
    import json
    try:
        data = json.loads(file.read().decode('utf-8'))
        import_backup(request.user, data)
        messages.success(request, 'Backup importado com sucesso.')
    except Exception as exc:
        messages.error(request, f'Erro ao importar: {exc}')
    return redirect('backup')


FORM_MAP = {
    'conta': (Conta, ContaForm, 'contas_list'),
    'cartao': (Cartao, CartaoForm, 'cartoes_list'),
    'categoria-receita': (Categoria, lambda u, **kw: CategoriaForm(u, Categoria.TIPO_RECEITA, **kw), 'categorias_list'),
    'categoria-despesa': (Categoria, lambda u, **kw: CategoriaForm(u, Categoria.TIPO_DESPESA, **kw), 'categorias_list'),
    'receita': (Receita, ReceitaForm, 'receitas_list'),
    'despesa': (Despesa, DespesaForm, 'despesas_list'),
    'investimento': (Investimento, InvestimentoForm, 'investimentos_list'),
    'bem': (Bem, BemForm, 'bens_list'),
    'orcamento': (Orcamento, OrcamentoForm, 'previsao'),
}


@login_required
def entity_form(request, entity, pk=None):
    if entity not in FORM_MAP:
        return HttpResponse(status=404)
    model_cls, form_cls, redirect_name = FORM_MAP[entity]
    instance = get_object_or_404(model_cls, pk=pk, user=request.user) if pk else None

    if request.method == 'POST':
        if callable(form_cls) and entity.startswith('categoria'):
            form = form_cls(request.user, request.POST, instance=instance)
        elif form_cls in (ContaForm, BemForm):
            form = form_cls(request.POST, instance=instance)
        else:
            form = form_cls(request.user, request.POST, instance=instance)
        if form.is_valid():
            obj = save_with_user(form, request.user)
            if entity == 'categoria-receita':
                obj.tipo = Categoria.TIPO_RECEITA
                obj.save(update_fields=['tipo'])
            elif entity == 'categoria-despesa':
                obj.tipo = Categoria.TIPO_DESPESA
                obj.save(update_fields=['tipo'])
            elif entity == 'despesa' and not pk:
                parcelas = form.cleaned_data.get('parcelas', 1)
                if (
                    obj.tipo == Despesa.TIPO_VARIAVEL
                    and obj.forma_pagamento == Despesa.FORMA_CARTAO
                    and parcelas > 1
                ):
                    obj.delete()
                    criar_despesa_parcelada(request.user, obj, parcelas)
                elif obj.tipo == Despesa.TIPO_VARIAVEL and form.cleaned_data.get('repetir'):
                    obj.delete()
                    criar_lancamento_repetido(
                        request.user, Despesa, obj, form.cleaned_data.get('vezes_repetir', 2)
                    )
            elif entity == 'receita' and not pk and obj.tipo == Receita.TIPO_VARIAVEL and form.cleaned_data.get('repetir'):
                obj.delete()
                criar_lancamento_repetido(
                    request.user, Receita, obj, form.cleaned_data.get('vezes_repetir', 2)
                )
            msg = 'Registro salvo com sucesso.'
            if request.htmx:
                return toast_response(request, msg, reverse(redirect_name))
            messages.success(request, msg)
            return redirect(redirect_name)
    else:
        if callable(form_cls) and entity.startswith('categoria'):
            form = form_cls(request.user, instance=instance)
        elif form_cls in (ContaForm, BemForm):
            form = form_cls(instance=instance)
        else:
            form = form_cls(request.user, instance=instance)

    return render(request, 'financas/partials/modal_form.html', {
        'form': form,
        'entity': entity,
        'instance': instance,
        'title': f"{'Editar' if instance else 'Novo'} — {entity.replace('-', ' ').title()}",
    })


@login_required
@require_POST
def entity_delete(request, entity, pk):
    if entity not in FORM_MAP:
        return HttpResponse(status=404)
    model_cls, _, redirect_name = FORM_MAP[entity]
    obj = get_object_or_404(model_cls, pk=pk, user=request.user)
    obj.delete()
    return toast_response(request, 'Registro excluído.', reverse(redirect_name))
