from django.urls import path
from .views import ChamadoListView

app_name = "chamados"

urlpatterns = [
    path("", ChamadoListView.as_view(), name="lista"),
]
