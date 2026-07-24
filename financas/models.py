import uuid

from django.conf import settings
from django.db import models


class UserOwnedModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
    )
    legacy_id = models.CharField(max_length=32, blank=True, db_index=True)

    class Meta:
        abstract = True


class Conta(UserOwnedModel):
    TIPO_CHOICES = [
        ('Conta Corrente', 'Conta Corrente'),
        ('Poupança', 'Poupança'),
        ('Dinheiro', 'Dinheiro'),
        ('Carteira Digital', 'Carteira Digital'),
        ('Outro', 'Outro'),
    ]

    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='Conta Corrente')
    saldo_inicial = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'

    def __str__(self):
        return self.nome


class Cartao(UserOwnedModel):
    nome = models.CharField(max_length=120)
    conta_pagamento = models.ForeignKey(
        Conta,
        on_delete=models.PROTECT,
        related_name='cartoes',
    )
    limite = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    dia_fechamento = models.PositiveSmallIntegerField()
    dia_vencimento = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['nome']
        verbose_name = 'Cartão'
        verbose_name_plural = 'Cartões'

    def __str__(self):
        return self.nome


class Categoria(UserOwnedModel):
    TIPO_RECEITA = 'receita'
    TIPO_DESPESA = 'despesa'
    TIPO_CHOICES = [
        (TIPO_RECEITA, 'Receita'),
        (TIPO_DESPESA, 'Despesa'),
    ]

    nome = models.CharField(max_length=120)
    cor = models.CharField(max_length=7, default='#0d9488')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    pai = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategorias',
    )

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class Receita(UserOwnedModel):
    TIPO_VARIAVEL = 'variavel'
    TIPO_FIXA = 'fixa'
    TIPO_CONSORCIO = 'consorcio'
    TIPO_CHOICES = [
        (TIPO_VARIAVEL, 'Variável'),
        (TIPO_FIXA, 'Fixa'),
        (TIPO_CONSORCIO, 'Consórcio'),
    ]

    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receitas',
    )
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='receitas')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_VARIAVEL)
    data = models.DateField(null=True, blank=True)
    dia_recebimento = models.PositiveSmallIntegerField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    numero_parcelas = models.PositiveIntegerField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    repeticao_id = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ['-data', 'descricao']
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'

    def __str__(self):
        return self.descricao


class Despesa(UserOwnedModel):
    FORMA_CONTA = 'conta'
    FORMA_CARTAO = 'cartao'
    FORMA_CHOICES = [
        (FORMA_CONTA, 'Débito em conta'),
        (FORMA_CARTAO, 'Cartão de crédito'),
    ]
    TIPO_VARIAVEL = 'variavel'
    TIPO_FIXA = 'fixa'
    TIPO_CONSORCIO = 'consorcio'
    TIPO_CHOICES = [
        (TIPO_VARIAVEL, 'Variável'),
        (TIPO_FIXA, 'Fixa'),
        (TIPO_CONSORCIO, 'Consórcio'),
    ]

    descricao = models.CharField(max_length=200)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despesas',
    )
    forma_pagamento = models.CharField(max_length=10, choices=FORMA_CHOICES, default=FORMA_CONTA)
    conta = models.ForeignKey(
        Conta,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='despesas',
    )
    cartao = models.ForeignKey(
        Cartao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='despesas',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_VARIAVEL)
    valor = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    valor_fixo = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    data = models.DateField(null=True, blank=True)
    dia_vencimento = models.PositiveSmallIntegerField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    numero_parcelas = models.PositiveIntegerField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    compra_id = models.CharField(max_length=32, blank=True)
    parcela_atual = models.PositiveIntegerField(null=True, blank=True)
    parcela_total = models.PositiveIntegerField(null=True, blank=True)
    repeticao_id = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ['-data', 'descricao']
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'

    def __str__(self):
        return self.descricao


class Investimento(UserOwnedModel):
    OPERACAO_APORTE = 'aporte'
    OPERACAO_RESGATE = 'resgate'
    OPERACAO_CHOICES = [
        (OPERACAO_APORTE, 'Aporte'),
        (OPERACAO_RESGATE, 'Resgate'),
    ]

    descricao = models.CharField(max_length=200)
    tipo_investimento = models.CharField(max_length=40, default='Outro')
    operacao = models.CharField(max_length=10, choices=OPERACAO_CHOICES, default=OPERACAO_APORTE)
    ativo_grupo = models.CharField(max_length=120, blank=True)
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name='investimentos')
    data = models.DateField()
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    valor_estimado_atual = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-data', 'descricao']
        verbose_name = 'Investimento'
        verbose_name_plural = 'Investimentos'

    def __str__(self):
        return self.descricao


class Bem(UserOwnedModel):
    TIPO_CHOICES = [
        ('Terreno', 'Terreno'),
        ('Imóvel', 'Imóvel'),
        ('Veículo', 'Veículo'),
        ('Outro', 'Outro'),
    ]

    descricao = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Terreno')
    data_aquisicao = models.DateField(null=True, blank=True)
    valor_aquisicao = models.DecimalField(max_digits=14, decimal_places=2)
    valor_estimado_atual = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['descricao']
        verbose_name = 'Bem'
        verbose_name_plural = 'Bens'

    def __str__(self):
        return self.descricao


class Orcamento(UserOwnedModel):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        limit_choices_to={'tipo': Categoria.TIPO_DESPESA},
        related_name='orcamentos',
    )
    valor_planejado = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        ordering = ['categoria__nome']
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        unique_together = [('user', 'categoria')]

    def __str__(self):
        return f'{self.categoria.nome}: {self.valor_planejado}'


def gerar_legacy_id():
    return uuid.uuid4().hex[:16]
