from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BackupExportAPIView,
    BackupImportAPIView,
    BemViewSet,
    CartaoViewSet,
    CategoriaViewSet,
    ContaViewSet,
    DashboardAPIView,
    DespesaViewSet,
    FaturasAPIView,
    InvestimentoViewSet,
    OrcamentoViewSet,
    PrevisaoAPIView,
    ReceitaViewSet,
    SaldoAPIView,
)

router = DefaultRouter()
router.register('contas', ContaViewSet, basename='conta')
router.register('cartoes', CartaoViewSet, basename='cartao')
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('receitas', ReceitaViewSet, basename='receita')
router.register('despesas', DespesaViewSet, basename='despesa')
router.register('investimentos', InvestimentoViewSet, basename='investimento')
router.register('bens', BemViewSet, basename='bem')
router.register('orcamentos', OrcamentoViewSet, basename='orcamento')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
    path('saldo/', SaldoAPIView.as_view(), name='api-saldo'),
    path('previsao/', PrevisaoAPIView.as_view(), name='api-previsao'),
    path('faturas/', FaturasAPIView.as_view(), name='api-faturas'),
    path('backup/export/', BackupExportAPIView.as_view(), name='api-backup-export'),
    path('backup/import/', BackupImportAPIView.as_view(), name='api-backup-import'),
]
