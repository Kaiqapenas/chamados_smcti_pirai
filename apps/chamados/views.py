from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy


from apps.chamados.forms import ChamadoForm
from .models import Chamado, AlteracaoChamado, ItemChamado
from .forms import ItemChamadoForm

class ChamadoListView(ListView):
    model = Chamado
    template_name = "chamados/lista.html"
    context_object_name = "chamados"

    def get_queryset(self):
        queryset = super().get_queryset()
        #filtro por status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        #filtro por urgencia
        urgencia = self.request.GET.get("urgencia")        
        if urgencia:
            queryset = queryset.filter(urgencia=urgencia)
        #busca por protocolo
        protocolo = self.request.GET.get("protocolo")
        if protocolo:
            queryset = queryset.filter(numero_protocolo__icontains=protocolo)
        return queryset
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        #passa as opções de filtro pro template
        context["status_choices"] = Chamado.Status.choices
        context["urgencia_choices"] = Chamado.Urgencia.choices
        return context
        
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
    model = Chamado
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        chamado.delete()
        return redirect("chamados:lista")

#ITENS DO CHAMADO
class ItemChamadoCreateView(CreateView):
    model = ItemChamado
    form_class = ItemChamadoForm
    template_name = "chamados/item_form.html"

    def form_valid(self, form):
        # Associa o item ao chamado da URL automaticamente
        form.instance.chamado_id = self.kwargs["chamado_pk"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("chamados:detalhe", kwargs={"pk": self.kwargs["chamado_pk"]})

class ItemChamadoUpdateView(UpdateView):
    model = ItemChamado
    form_class = ItemChamadoForm
    template_name = "chamados/item_form.html"

    def get_success_url(self):
        return reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk})

class ItemChamadoDeleteView(DeleteView):
    model = ItemChamado
    template_name = "chamados/confirmar_remocao.html"

    def get_success_url(self):
        return reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk})

