"""Ponto de entrada WSGI na raiz do projeto (Render)."""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from config.wsgi import application

__all__ = ['application']
