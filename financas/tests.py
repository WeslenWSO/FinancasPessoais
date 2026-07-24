from decimal import Decimal
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from financas.models import Cartao, Categoria, Conta, Despesa, Orcamento, Receita, gerar_legacy_id
from financas.services.faturas import competencia_base, faturas_do_cartao, vencimento_da_fatura
from financas.services.previsao import get_previsao
from financas.services.saldo import saldo_conta_ate_hoje, saldo_total_hoje
from financas.signals import criar_categorias_padrao


class FinancasServicesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teste', password='teste123')
        criar_categorias_padrao(self.user)
        self.conta = Conta.objects.create(
            user=self.user,
            legacy_id=gerar_legacy_id(),
            nome='Conta Teste',
            saldo_inicial=Decimal('1000.00'),
        )
        self.cartao = Cartao.objects.create(
            user=self.user,
            legacy_id=gerar_legacy_id(),
            nome='Cartão Teste',
            conta_pagamento=self.conta,
            limite=Decimal('5000.00'),
            dia_fechamento=10,
            dia_vencimento=17,
        )
        self.cat_despesa = Categoria.objects.filter(user=self.user, tipo=Categoria.TIPO_DESPESA).first()

    def test_saldo_conta_com_receita_variavel(self):
        Receita.objects.create(
            user=self.user,
            legacy_id=gerar_legacy_id(),
            descricao='Salário extra',
            valor=Decimal('500.00'),
            conta=self.conta,
            tipo=Receita.TIPO_VARIAVEL,
            data=date.today(),
        )
        saldo = saldo_conta_ate_hoje(self.user, self.conta.pk)
        self.assertEqual(saldo, Decimal('1500.00'))

    def test_competencia_fatura_apos_fechamento(self):
        comp = competencia_base(self.cartao, '2026-03-05')
        self.assertEqual(comp, '2026-03')
        comp2 = competencia_base(self.cartao, '2026-03-11')
        self.assertEqual(comp2, '2026-04')

    def test_fatura_parcelada_cartao(self):
        Despesa.objects.create(
            user=self.user,
            legacy_id=gerar_legacy_id(),
            descricao='Compra parcelada 1/2',
            categoria=self.cat_despesa,
            forma_pagamento=Despesa.FORMA_CARTAO,
            cartao=self.cartao,
            tipo=Despesa.TIPO_VARIAVEL,
            valor=Decimal('100.00'),
            data=date(2026, 3, 5),
            parcela_atual=1,
            parcela_total=2,
        )
        Despesa.objects.create(
            user=self.user,
            legacy_id=gerar_legacy_id(),
            descricao='Compra parcelada 2/2',
            categoria=self.cat_despesa,
            forma_pagamento=Despesa.FORMA_CARTAO,
            cartao=self.cartao,
            tipo=Despesa.TIPO_VARIAVEL,
            valor=Decimal('100.00'),
            data=date(2026, 3, 5),
            parcela_atual=2,
            parcela_total=2,
        )
        faturas = faturas_do_cartao(self.user, self.cartao.pk, 12)
        self.assertIn('2026-03', faturas)
        self.assertIn('2026-04', faturas)
        self.assertEqual(faturas['2026-03']['total'], Decimal('100.00'))
        self.assertEqual(faturas['2026-04']['total'], Decimal('100.00'))

    def test_previsao_retorna_12_meses(self):
        linhas = get_previsao(self.user)
        self.assertEqual(len(linhas), 12)
        self.assertIn('saldo_acumulado', linhas[0])

    def test_vencimento_fatura(self):
        venc = vencimento_da_fatura(self.cartao, '2026-03')
        self.assertTrue(venc.endswith('-17') or venc.endswith('-16'))

    def test_saldo_total_soma_contas(self):
        saldo = saldo_total_hoje(self.user)
        self.assertEqual(saldo, Decimal('1000.00'))
