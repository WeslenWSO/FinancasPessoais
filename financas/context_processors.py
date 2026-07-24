from django.contrib.auth.decorators import login_required
from django.utils import timezone

from financas.services.saldo import saldo_total_hoje
from financas.utils import month_key


NAV_MAP = {
    'dashboard': 'dashboard',
    'contas_list': 'contas',
    'cartoes_list': 'cartoes',
    'faturas': 'faturas',
    'categorias_list': 'categorias',
    'receitas_list': 'receitas',
    'despesas_list': 'despesas',
    'investimentos_list': 'investimentos',
    'bens_list': 'bens',
    'previsao': 'previsao',
    'backup': 'backup',
    'backup_export': 'backup',
    'backup_import': 'backup',
}

NAV_TITLES = {
    'dashboard': 'Dashboard',
    'contas': 'Contas',
    'cartoes': 'Cartões',
    'faturas': 'Faturas',
    'categorias': 'Categorias',
    'receitas': 'Receitas',
    'despesas': 'Despesas',
    'investimentos': 'Investimentos',
    'bens': 'Bens',
    'previsao': 'Previsão',
    'backup': 'Backup',
}


def sidebar_context(request):
    if not request.user.is_authenticated:
        return {}
    url_name = getattr(getattr(request, 'resolver_match', None), 'url_name', '')
    return {
        'sidebar_saldo': saldo_total_hoje(request.user),
        'current_month': month_key(timezone.localdate()),
        'active_nav': NAV_MAP.get(url_name, ''),
        'page_title': NAV_TITLES.get(NAV_MAP.get(url_name, ''), 'Finanças Pessoais'),
    }
