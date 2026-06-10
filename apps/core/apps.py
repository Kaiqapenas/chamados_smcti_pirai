from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'

    def ready(self):
        # Importa sinais para associar automaticamente privilégios
        # quando um superuser é criado via createsuperuser
        import apps.core.signals  # noqa: F401
