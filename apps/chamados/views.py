from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from apps.chamados.forms import ChamadoForm
from .models import Chamado


class ChamadoListView(ListView):
    model = Chamado
    template_name = "chamados/lista.html"
    context_object_name = "chamados"

class ChamadoCreateView(View):
    def get(self, request):
        form = ChamadoForm()
        return render(request, "chamados/form.html", {"form": form})

    def post(self, request):
        form = ChamadoForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("chamados:lista")

        return render(request, "chamados/form.html", {"form": form})
    
class ChamadoDetailView(DetailView):
    model = Chamado
    template_name = "chamados/detalhe.html"
    context_object_name = "chamado"
    
class ChamadoUpdateView(View):
    def get(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        form = ChamadoForm(instance=chamado)
        return render(request, "chamados/form.html", {"form": form, "chamado": chamado})

    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        form = ChamadoForm(request.POST, instance=chamado)

        if form.is_valid():
            form.save()
            return redirect("chamados:detalhe", pk=pk)

        return render(request, "chamados/form.html", {"form": form, "chamado": chamado})

class ChamadoDeleteView(View):
    def get(self, request, pk):  # ⚠️ não recomendado
        chamado = get_object_or_404(Chamado, pk=pk)
        chamado.delete()
        return redirect("chamados:lista")

    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        chamado.delete()
        return redirect("chamados:lista")

