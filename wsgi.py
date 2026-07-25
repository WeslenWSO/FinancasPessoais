"""Ponto de entrada WSGI na raiz do projeto (Render)."""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

_IS_RENDER = os.environ.get('RENDER', '').lower() in ('true', '1', 'yes') or bool(
    os.environ.get('RENDER_EXTERNAL_HOSTNAME')
)


def _deploy_log(message: str) -> None:
    print(f'[deploy] {message}', file=sys.stderr, flush=True)


if _IS_RENDER:
    import django

    django.setup()
    from django.conf import settings
    from django.core.management import call_command

    db = settings.DATABASES['default']
    _deploy_log(f'database engine={db["ENGINE"]} name={db.get("NAME", "?")}')

    if not os.environ.get('DATABASE_URL'):
        _deploy_log(
            'AVISO: DATABASE_URL ausente — migrate em SQLite (ephemeral). '
            'Configure PostgreSQL no Dashboard Render.',
        )

    _deploy_log('executando migrate...')
    try:
        call_command('migrate', '--noinput', verbosity=1)
    except Exception:
        _deploy_log('ERRO: migrate falhou — veja traceback acima')
        raise
    _deploy_log('migrate concluído')

    if os.environ.get('DJANGO_SUPERUSER_USERNAME'):
        _deploy_log('executando ensure_superuser...')
        call_command('ensure_superuser', verbosity=1)

from config.wsgi import application

__all__ = ['application']
