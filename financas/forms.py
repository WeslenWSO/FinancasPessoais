from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from financas.models import (
    Bem,
    Cartao,
    Categoria,
    Conta,
    Despesa,
    Investimento,
    Orcamento,
    Receita,
    gerar_legacy_id,
)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ['nome', 'tipo', 'saldo_inicial']
        widgets = {
            'saldo_inicial': forms.NumberInput(attrs={'step': '0.01'}),
        }


class CartaoForm(forms.ModelForm):
    class Meta:
        model = Cartao
        fields = ['nome', 'conta_pagamento', 'limite', 'dia_fechamento', 'dia_vencimento']
        widgets = {
            'limite': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conta_pagamento'].queryset = Conta.objects.filter(user=user)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'cor', 'pai']
        widgets = {'cor': forms.TextInput(attrs={'type': 'color'})}

    def __init__(self, user, tipo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pai'].queryset = Categoria.objects.filter(user=user, tipo=tipo, pai__isnull=True)
        self.fields['pai'].required = False


class ReceitaForm(forms.ModelForm):
    repetir = forms.BooleanField(required=False, label='Repetir por vários meses')
    vezes_repetir = forms.IntegerField(required=False, min_value=2, max_value=60, initial=2)

    class Meta:
        model = Receita
        fields = [
            'descricao', 'valor', 'categoria', 'conta', 'tipo', 'data',
            'dia_recebimento', 'data_inicio', 'data_fim', 'numero_parcelas', 'ativa',
        ]
        widgets = {
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
            'data': forms.DateInput(attrs={'type': 'date'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conta'].queryset = Conta.objects.filter(user=user)
        self.fields['categoria'].queryset = Categoria.objects.filter(user=user, tipo=Categoria.TIPO_RECEITA)
        self.fields['categoria'].required = False
        self.fields['data'].required = False
        self.fields['dia_recebimento'].required = False
        self.fields['data_inicio'].required = False
        self.fields['data_fim'].required = False
        self.fields['numero_parcelas'].required = False
        self.fields['ativa'].required = False


class DespesaForm(forms.ModelForm):
    repetir = forms.BooleanField(required=False, label='Repetir por vários meses')
    vezes_repetir = forms.IntegerField(required=False, min_value=2, max_value=60, initial=2)
    parcelas = forms.IntegerField(required=False, min_value=1, max_value=60, initial=1, label='Número de parcelas')

    class Meta:
        model = Despesa
        fields = [
            'descricao', 'categoria', 'forma_pagamento', 'conta', 'cartao', 'tipo',
            'valor', 'valor_fixo', 'data', 'dia_vencimento', 'data_inicio', 'data_fim',
            'numero_parcelas', 'ativa',
        ]
        widgets = {
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
            'valor_fixo': forms.NumberInput(attrs={'step': '0.01'}),
            'data': forms.DateInput(attrs={'type': 'date'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conta'].queryset = Conta.objects.filter(user=user)
        self.fields['cartao'].queryset = Cartao.objects.filter(user=user)
        self.fields['categoria'].queryset = Categoria.objects.filter(user=user, tipo=Categoria.TIPO_DESPESA)
        self.fields['categoria'].required = False
        self.fields['conta'].required = False
        self.fields['cartao'].required = False
        self.fields['data'].required = False
        self.fields['valor'].required = False
        self.fields['valor_fixo'].required = False
        self.fields['dia_vencimento'].required = False
        self.fields['data_inicio'].required = False
        self.fields['data_fim'].required = False
        self.fields['numero_parcelas'].required = False
        self.fields['ativa'].required = False


class InvestimentoForm(forms.ModelForm):
    class Meta:
        model = Investimento
        fields = [
            'descricao', 'tipo_investimento', 'operacao', 'ativo_grupo',
            'conta', 'data', 'valor', 'valor_estimado_atual',
        ]
        widgets = {
            'valor': forms.NumberInput(attrs={'step': '0.01'}),
            'valor_estimado_atual': forms.NumberInput(attrs={'step': '0.01'}),
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['conta'].queryset = Conta.objects.filter(user=user)
        self.fields['ativo_grupo'].required = False
        self.fields['valor_estimado_atual'].required = False


class BemForm(forms.ModelForm):
    class Meta:
        model = Bem
        fields = ['descricao', 'tipo', 'data_aquisicao', 'valor_aquisicao', 'valor_estimado_atual']
        widgets = {
            'valor_aquisicao': forms.NumberInput(attrs={'step': '0.01'}),
            'valor_estimado_atual': forms.NumberInput(attrs={'step': '0.01'}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_aquisicao'].required = False
        self.fields['valor_estimado_atual'].required = False


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ['categoria', 'valor_planejado']
        widgets = {'valor_planejado': forms.NumberInput(attrs={'step': '0.01'})}

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usadas = Orcamento.objects.filter(user=user).values_list('categoria_id', flat=True)
        qs = Categoria.objects.filter(user=user, tipo=Categoria.TIPO_DESPESA)
        if self.instance.pk:
            qs = qs.filter(pk=self.instance.categoria_id) | qs.exclude(pk__in=usadas)
        else:
            qs = qs.exclude(pk__in=usadas)
        self.fields['categoria'].queryset = qs


def save_with_user(form, user, legacy=True):
    obj = form.save(commit=False)
    obj.user = user
    if legacy and not obj.legacy_id:
        obj.legacy_id = gerar_legacy_id()
    obj.save()
    return obj
