from django.urls import path
from .views import CategoriaEstoqueListView, EstoqueListView, EstoqueCreateView, EstoqueUpdateView, EstoqueDeleteView, CategoriaEstoqueCreateView, CategoriaEstoqueUpdateView, CategoriaEstoqueDeleteView, MovimentacaoEstoqueCreateView, MovimentacaoEstoqueListView, MovimentacaoEstoqueUpdateView, MovimentacaoEstoqueDeleteView

app_name = "estoque"

urlpatterns = [
    path("", EstoqueListView.as_view(), name="lista"),

    path("adicionar/", EstoqueCreateView.as_view(), name="adicionar"),
    path("<int:pk>/editar/", EstoqueUpdateView.as_view(), name="editar"),
    path("<int:pk>/remover/", EstoqueDeleteView.as_view(), name="excluir"),

    # categoria
    path("categoria/", CategoriaEstoqueListView.as_view(), name="categoria_lista"),
    path("categoria/adicionar/", CategoriaEstoqueCreateView.as_view(), name="adicionar_categoria"),
    path("categoria/<int:pk>/editar/", CategoriaEstoqueUpdateView.as_view(), name="editar_categoria"),
    path("categoria/<int:pk>/remover/", CategoriaEstoqueDeleteView.as_view(), name="excluir_categoria"),

    # movimentação
    path("movimentacao/", MovimentacaoEstoqueListView.as_view(), name="movimentacao_lista"),
    path("movimentacao/adicionar/", MovimentacaoEstoqueCreateView.as_view(), name="adicionar_movimentacao"),
    path("movimentacao/<int:pk>/editar/", MovimentacaoEstoqueUpdateView.as_view(), name="editar_movimentacao"),
    path("movimentacao/<int:pk>/remover/", MovimentacaoEstoqueDeleteView.as_view(), name="excluir_movimentacao"),
    
]