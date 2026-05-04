from django.contrib import admin

from .models import AlteracaoChamado, Chamado, ItemChamado


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_protocolo",
        "titulo",
        "solicitante",
        "status",
        "urgencia",
        "usuario",
        "data_criacao",
    )
    list_filter = ("status", "urgencia")
    search_fields = ("titulo", "descricao", "numero_protocolo", "solicitante")
    raw_id_fields = ("usuario",)


@admin.register(ItemChamado)
class ItemChamadoAdmin(admin.ModelAdmin):
    list_display = ("chamado", "item", "quantidade", "usuario")
    search_fields = ("chamado__numero_protocolo", "item__nome")
    raw_id_fields = ("chamado", "item", "usuario")


@admin.register(AlteracaoChamado)
class AlteracaoChamadoAdmin(admin.ModelAdmin):
    list_display = (
        "chamado",
        "status_anterior",
        "status_novo",
        "usuario",
        "data_alteracao",
    )
    list_filter = ("status_novo",)
    search_fields = ("descricao", "chamado__numero_protocolo")
    raw_id_fields = ("chamado", "usuario")
