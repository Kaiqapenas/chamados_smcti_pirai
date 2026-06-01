from django.urls import path
from .views import ChamadoListView, ChamadoCreateView, ChamadoDetailView, ChamadoUpdateView, ChamadoDeleteView, ChamadoMudarStatusView, ItemChamadoCreateView, ItemChamadoDeleteView, ItemChamadoUpdateView, ChamadosAtribuidosView, ReatribuicaoTecnicoView 

app_name = "chamados"

urlpatterns = [
    # chamados
    path("", ChamadoListView.as_view(), name="index"),
    path("adicionar/", ChamadoCreateView.as_view(), name="adicionar"),
    path("<int:pk>/", ChamadoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", ChamadoUpdateView.as_view(), name="editar"),
    path("<int:pk>/remover/", ChamadoDeleteView.as_view(), name="remover"),
    path("<int:pk>/mudar_status/", ChamadoMudarStatusView.as_view(), name="mudar_status"),
    #chamado tecnico
    path("atribuidos/", ChamadosAtribuidosView.as_view(), name="atribuidos"),
    #itens do chamado
    path("<int:chamado_pk>/itens/adicionar/", ItemChamadoCreateView.as_view(), name="adicionar_item"),
    path("itens/<int:pk>/editar/", ItemChamadoUpdateView.as_view(), name="editar_item"),
    path("itens/<int:pk>/remover/", ItemChamadoDeleteView.as_view(), name="remover_item"),
    path("reatribuir/", ReatribuicaoTecnicoView.as_view(), name="reatribuir_tecnico"),
     # # ATENÇÃO: As views atuais são temporárias, mudar conforme forem implementadas
    # #alterações do chamado
    # path("<int:chamado_id>/alteracoes/", AlteracaoChamadoListView.as_view(), name="alteracao_lista"),
    # path("<int:chamado_id>/alteracoes/adicionar/", AlteracaoChamadoCreateView.as_view(), name="alteracao_adicionar"),
]
