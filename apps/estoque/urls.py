from django.urls import path
from .views import EstoqueListView

app_name = "estoque"

urlpatterns = [
    path("", EstoqueListView.as_view(), name="lista"),
    
    # Placeholder para criação de views para criar, editar e excluir Estoque
    path("estoque/adicionar/", EstoqueListView.as_view(), name="adicionar"),
    path("<int:pk>/", ItemEstoqueDetailView.as_view(), name="detalhe"),
    path("<int:pk>/", EstoqueListView.as_view(), name="editar"),
    path("<int:pk>/", EstoqueListView.as_view(), name="excluir"),
    
    # Placeholder para criação de views para criar, editar e excluir categoria de estoque
    path("categoria/adicionar/", EstoqueListView.as_view(), name="adicionar_categoria"),
    path("categoria/<int:pk>/editar/", EstoqueListView.as_view(), name="editar_categoria"),
    path("categoria/<int:pk>/excluir/", EstoqueListView.as_view(), name="excluir_categoria"),
    
    # Placeholder para criação de views para criar, editar e excluir MovimentaçãoEstoque
    path("movimentacao/adicionar/", EstoqueListView.as_view(), name="adicionar_movimentacao"),
    path("movimentacao/<int:pk>/editar/", EstoqueListView.as_view(), name="editar_movimentacao"),
    path("movimentacao/<int:pk>/excluir/", EstoqueListView.as_view(), name="excluir_movimentacao"),

    # ItemImagem
    path("<int:item_pk>/imagens/adicionar/", ItemImagemCreateView.as_view(), name="imagem_adicionar"),
    path("imagens/<int:pk>/remover/", ItemImagemDeleteView.as_view(), name="imagem_remover"),
]