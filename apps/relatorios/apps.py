from django.apps import AppConfig


class RelatoriosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore[assignment]
    name = 'apps.relatorios'
    verbose_name = 'Relatórios'
