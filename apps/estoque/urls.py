from django.urls import path
from .views import EstoqueListView

app_name = "estoque"

urlpatterns = [
    path("", EstoqueListView.as_view(), name="lista"),
    
    # Placeholder para criação de views para criar, editar e excluir Estoque
    path("estoque/adicionar/", EstoqueListView.as_view(), name="adicionar"),
    path("estoque/editar/<int:id>/", EstoqueListView.as_view(), name="editar"),
    path("estoque/excluir/<int:id>/", EstoqueListView.as_view(), name="excluir"),
    
    # Placeholder para criação de views para criar, editar e excluir categoria de estoque
    path("categoria/adicionar/", EstoqueListView.as_view(), name="adicionar_categoria"),
    path("categoria/editar/<int:id>/", EstoqueListView.as_view(), name="editar_categoria"),
    path("categoria/excluir/<int:id>/", EstoqueListView.as_view(), name="excluir_categoria"),
    
    # Placeholder para criação de views para criar, editar e excluir MovimentaçãoEstoque
    path("movimentacao/adicionar/", EstoqueListView.as_view(), name="adicionar_movimentacao"),
    path("movimentacao/editar/<int:id>/", EstoqueListView.as_view(), name="editar_movimentacao"),
    path("movimentacao/excluir/<int:id>/", EstoqueListView.as_view(), name="excluir_movimentacao"),

]