"""Ponto de entrada WSGI na raiz do projeto (Render)."""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if os.environ.get('RENDER'):
    import django

    django.setup()
    from django.core.management import call_command

    call_command('migrate', '--noinput', verbosity=0)
    if os.environ.get('DJANGO_SUPERUSER_USERNAME'):
        call_command('ensure_superuser', verbosity=0)

from config.wsgi import application

__all__ = ['application']
