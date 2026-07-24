from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods

from financas.forms import RegisterForm
from financas.signals import criar_categorias_padrao


class CustomLoginView(LoginView):
    template_name = 'financas/auth/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            criar_categorias_padrao(user)
            login(request, user)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'financas/auth/register.html', {'form': form})


from financas.models import Despesa, Receita, gerar_legacy_id


def criar_despesa_parcelada(user, base, parcelas):
    n = int(parcelas or 1)
    valor_total = Decimal(str(base.valor))
    valor_parcela = (valor_total / n).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    compra_id = gerar_legacy_id()
    restante = valor_total

    for i in range(1, n + 1):
        if i == n:
            v = restante.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            v = valor_parcela
            restante -= v
        Despesa.objects.create(
            user=user,
            legacy_id=gerar_legacy_id(),
            descricao=f'{base.descricao} ({i}/{n})',
            categoria=base.categoria,
            forma_pagamento=Despesa.FORMA_CARTAO,
            cartao=base.cartao,
            tipo=Despesa.TIPO_VARIAVEL,
            valor=v,
            data=base.data,
            compra_id=compra_id,
            parcela_atual=i,
            parcela_total=n,
        )


def criar_lancamento_repetido(user, model_cls, base, vezes):
    repeticao_id = gerar_legacy_id()
    data_base = base.data
    for i in range(int(vezes)):
        obj = model_cls(
            user=user,
            legacy_id=gerar_legacy_id(),
            descricao=base.descricao,
            categoria=base.categoria,
            conta=base.conta,
            tipo=base.tipo,
            valor=base.valor,
            data=data_base + timedelta(days=30 * i) if data_base else None,
            repeticao_id=repeticao_id,
        )
        if model_cls.__name__ == 'Despesa':
            obj.forma_pagamento = base.forma_pagamento
        obj.save()
