from django.views.generic import ListView
from .models import Estoque


class EstoqueListView(ListView):
    model = Estoque
    template_name = "estoque/lista.html"
    context_object_name = "estoques"