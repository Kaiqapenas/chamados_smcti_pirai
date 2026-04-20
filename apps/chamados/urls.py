from django.urls import path
from .views import *

app_name = "chamados"

urlpatterns = [
    # chamados
    path("", ChamadoListView.as_view(), name="lista"),
    #itens do chamado
    # ATENÇÃO: As views atuais são temporárias, mudar conforme forem implementadas
    path("itens/", ChamadoListView.as_view(), name="item_lista"),
    path("itens/adicionar/", ChamadoListView.as_view(), name="item_add"),
    path("itens/<int:id>/remover/", ChamadoListView.as_view(), name="item_remove"),
    path("itens/<int:id>/editar/", ChamadoListView.as_view(), name="item_edit"),
]
