from django.views.generic import ListView
from .models import ItemEstoque


class EstoqueListView(ListView):
    model = ItemEstoque
    template_name = "estoque/lista.html"
    context_object_name = "estoques"