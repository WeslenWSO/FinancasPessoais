from django.apps import AppConfig


class FinancasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'financas'
    verbose_name = 'Finanças Pessoais'

    def ready(self):
        import financas.signals  # noqa: F401
