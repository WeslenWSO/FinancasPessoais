from django.contrib import admin

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


@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'saldo_inicial', 'user')
    list_filter = ('tipo',)


@admin.register(Cartao)
class CartaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'conta_pagamento', 'limite', 'user')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'cor', 'user')


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'tipo', 'data', 'user')


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'tipo', 'forma_pagamento', 'data', 'user')


@admin.register(Investimento)
class InvestimentoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'operacao', 'valor', 'data', 'user')


@admin.register(Bem)
class BemAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'valor_aquisicao', 'user')


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'valor_planejado', 'user')
