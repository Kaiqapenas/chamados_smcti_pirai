from django.urls import path
from .views import *

app_name = "chamados"

urlpatterns = [
    # chamados
    path("", ChamadoListView.as_view(), name="lista"),
    #itens do chamado
    path("itens/", ItemChamadoListView.as_view(), name="item_lista"),
    path("itens/adicionar/", ItemChamadoCreateView.as_view(), name="item_add"),
    path("itens/<int:id>/remover/", ItemChamadoDeleteView.as_view(), name="item_remove"),
    path("itens/<int:id>/editar/", ItemChamadoUpdateView.as_view(), name="item_edit"),
]
