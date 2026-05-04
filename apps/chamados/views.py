from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

from apps.chamados.forms import ChamadoForm
from .models import Chamado, AlteracaoChamado, ItemChamado
from .forms import ItemChamadoForm

class ChamadoListView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "chamados/lista.html"
    context_object_name = "chamados"

    def get_queryset(self):
        #para evitar N queries no template
        queryset = super().get_queryset().select_related().prefetch_related("itens")
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
        
class ChamadoCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ChamadoForm()
        return render(request, "chamados/form.html", {"form": form})

    def post(self, request):
        form = ChamadoForm(request.POST, request.FILES)

        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.usuario = request.user
            chamado.save()
            messages.success(request, "Chamado criado com sucesso")
            return redirect("chamados:lista")

        return render(request, "chamados/form.html", {"form": form})
    
class ChamadoDetailView(LoginRequiredMixin, DetailView):
    model = Chamado
    template_name = "chamados/detalhe.html"
    context_object_name = "chamado"
    
class ChamadoUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        if chamado.status == Chamado.Status.FINALIZADO:
            messages.error(request, "Não é possível editar um chamado finalizado.")
            return redirect("chamados:detalhe", pk=pk)
        form = ChamadoForm(instance=chamado)
        return render(request, "chamados/form.html", {"form": form, "chamado": chamado})

    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        if chamado.status == Chamado.Status.FINALIZADO:
            messages.error(request, "Não é possível editar um chamado finalizado.")
            return redirect("chamados:detalhe", pk=pk)
        form = ChamadoForm(request.POST, instance=chamado)

        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.usuario = request.user
            chamado.save()
            messages.success(request, "Chamado atualizado com sucesso.")
            return redirect("chamados:detalhe", pk=pk)

        return render(request, "chamados/form.html", {"form": form, "chamado": chamado})

class ChamadoDeleteView(LoginRequiredMixin, View):
    model = Chamado
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        chamado.delete()
        return redirect("chamados:lista")

class ChamadoMudarStatusView(View):
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        novo_status = request.POST.get("status")

        if novo_status not in Chamado.Status.values:
            messages.error(request, "Status inválido")
            return redirect("chamados:detalhe", pk=pk)

        try:
            chamado.mudar_status(novo_status, request.user)
            messages.success(request, f"Status alterado para {chamado.get_status_display()}")
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect("chamados:detalhe", pk=pk)

#ITENS DO CHAMADO
class ItemChamadoCreateView(LoginRequiredMixin, CreateView):
    model = ItemChamado
    form_class = ItemChamadoForm
    template_name = "chamados/item_form.html"

    def form_valid(self, form):
        # Associa o item ao chamado da URL automaticamente
        chamado = get_object_or_404(Chamado, pk = self.kwargs["chamado_pk"])
        form.instance.chamado = chamado
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("chamados:detalhe", kwargs={"pk": self.kwargs["chamado_pk"]})

class ItemChamadoUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemChamado
    form_class = ItemChamadoForm
    template_name = "chamados/item_form.html"

    def get_success_url(self):
        return reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk})

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class ItemChamadoDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemChamado
    template_name = "chamados/confirmar_remocao.html"

    def post(self,request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Item removido com sucesso.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk})

