from django.contrib import admin

from .models import CategoriaItem, ItemEstoque, ItemImagem, MovimentacaoEstoque


@admin.register(CategoriaItem)
class CategoriaItemAdmin(admin.ModelAdmin):
    list_display = ("nome", "usuario")
    search_fields = ("nome",)


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "quantidade",
        "quantidade_minima",
        "ativo",
        "usuario",
        "data_criacao",
    )
    list_filter = ("categoria", "ativo", "unidade_medida")
    search_fields = ("nome", "patrimonio", "marca", "modelo")
    raw_id_fields = ("categoria", "usuario")


@admin.register(ItemImagem)
class ItemImagemAdmin(admin.ModelAdmin):
    list_display = ("produto", "ordem", "is_principal", "usuario")
    list_filter = ("is_principal",)
    raw_id_fields = ("produto", "usuario")


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ("item", "tipo", "quantidade", "protocolo", "usuario", "data_movimentacao")
    list_filter = ("tipo",)
    search_fields = ("observacao", "item__nome")
    raw_id_fields = ("item", "protocolo", "usuario")
