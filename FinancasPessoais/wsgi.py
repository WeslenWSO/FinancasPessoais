"""Alias para compatibilidade com Render (gunicorn FinancasPessoais.wsgi:application)."""

from config.wsgi import application

__all__ = ['application']
