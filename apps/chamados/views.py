from django.views.generic import ListView
from .models import Chamado


class ChamadoListView(ListView):
    model = Chamado
    template_name = "chamados/lista.html"
    context_object_name = "chamados"
