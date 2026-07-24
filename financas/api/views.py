import json

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
from financas.services.backup import export_backup, import_backup
from financas.services.dashboard import get_dashboard_data
from financas.services.faturas import faturas_do_cartao
from financas.services.previsao import get_previsao
from financas.services.saldo import saldo_total_hoje
from financas.utils import month_key
from django.utils import timezone

from .serializers import (
    BemSerializer,
    CartaoSerializer,
    CategoriaSerializer,
    ContaSerializer,
    DespesaSerializer,
    InvestimentoSerializer,
    OrcamentoSerializer,
    ReceitaSerializer,
)


class UserQuerysetMixin:
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ContaViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ContaSerializer
    queryset = Conta.objects.all()


class CartaoViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CartaoSerializer
    queryset = Cartao.objects.all()


class CategoriaViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    queryset = Categoria.objects.all()


class ReceitaViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ReceitaSerializer
    queryset = Receita.objects.all()


class DespesaViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = DespesaSerializer
    queryset = Despesa.objects.all()


class InvestimentoViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = InvestimentoSerializer
    queryset = Investimento.objects.all()


class BemViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = BemSerializer
    queryset = Bem.objects.all()


class OrcamentoViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = OrcamentoSerializer
    queryset = Orcamento.objects.all()


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ym = request.query_params.get('mes') or month_key(timezone.localdate())
        data = get_dashboard_data(request.user, ym)
        return Response({
            'ym': ym,
            'saldo_total': float(data['saldo_total']),
            'total_receitas': float(data['total_receitas']),
            'total_despesas': float(data['total_despesas']),
            'saldo_mes': float(data['saldo_mes']),
            'investido_atual': float(data['investido_atual']),
            'patrimonio_bens': float(data['patrimonio_bens']),
            'chart_labels': data['chart_labels'],
            'serie_receita': data['serie_receita'],
            'serie_despesa': data['serie_despesa'],
            'donut_data': data['donut_data'],
        })


class SaldoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'saldo_total': float(saldo_total_hoje(request.user))})


class PrevisaoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        linhas = get_previsao(request.user)
        return Response([
            {k: float(v) if hasattr(v, 'quantize') else v for k, v in linha.items()}
            for linha in linhas
        ])


class FaturasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cartao_id = request.query_params.get('cartao_id')
        mes = request.query_params.get('mes') or month_key(timezone.localdate())
        if not cartao_id:
            return Response({'detail': 'cartao_id obrigatório'}, status=400)
        faturas = faturas_do_cartao(request.user, int(cartao_id), 12)
        fat = faturas.get(mes, {'itens': [], 'total': 0})
        return Response({
            'mes': mes,
            'total': float(fat['total']),
            'itens': fat['itens'],
        })


class BackupExportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = json.dumps(export_backup(request.user), indent=2, ensure_ascii=False)
        response = HttpResponse(content, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="backup-financas.json"'
        return response


class BackupImportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        if isinstance(data, str):
            data = json.loads(data)
        import_backup(request.user, data)
        return Response({'detail': 'Backup importado com sucesso.'})
