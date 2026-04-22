from django.urls import path
from .views import ChamadoListView
from .views import ChamadoCreateView, ChamadoDetailView, ChamadoUpdateView, ChamadoDeleteView
from .views import *

app_name = "chamados"

urlpatterns = [
    # chamados
    path("", ChamadoListView.as_view(), name="lista"),
    path("adicionar/", ChamadoCreateView.as_view(), name="adicionar"),
    path("<int:pk>/", ChamadoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", ChamadoUpdateView.as_view(), name="editar"),
    path("<int:pk>/remover/", ChamadoDeleteView.as_view(), name="remover"),
    #itens do chamado
    # ATENÇÃO: As views atuais são temporárias, mudar conforme forem implementadas
    path("<int:chamado_id>/itens/adicionar/", ItemChamadoCreateView.as_view(), name="adicionar_item"),
    path("itens/<int:pk>/editar/", ItemChamadoUpdateView.as_view(), name="editar_item"),
    path("itens/<int:pk>/remover/", ItemChamadoDeleteView.as_view(), name="remover_item"),
    #alterações do chamado
    path("<int:chamado_id>/alteracoes/", AlteracaoChamadoListView.as_view(), name="alteracao_lista"),
    path("<int:chamado_id>/alteracoes/adicionar/", AlteracaoChamadoCreateView.as_view(), name="alteracao_adicionar"),
]
