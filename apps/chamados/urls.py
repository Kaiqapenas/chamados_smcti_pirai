from django.urls import path
from .views import ChamadoListView, ChamadoCreateView, ChamadoDetailView, ChamadoUpdateView, ChamadoDeleteView

app_name = "chamados"

urlpatterns = [
    # chamados
    path("", ChamadoListView.as_view(), name="lista"),
    path("adicionar/", ChamadoCreateView.as_view(), name="adicionar"),
    path("<int:pk>/", ChamadoDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", ChamadoUpdateView.as_view(), name="editar"),
    path("<int:pk>/remover/", ChamadoDeleteView.as_view(), name="remover"),
    #itens do chamado
]
