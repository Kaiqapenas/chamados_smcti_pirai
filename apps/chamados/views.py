from typing import TYPE_CHECKING, Any, cast

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

from apps.estoque.models import ItemEstoque
from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from django.db.models.manager import Manager

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
        return render(request, "chamados/cadastro.html", {"form": form})

    def post(self, request):
        form = ChamadoForm(request.POST, request.FILES)

        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.usuario = request.user
            chamado.save()
            messages.success(request, "Chamado criado com sucesso")
            return redirect("chamados:lista")

        return render(request, "chamados/cadastro.html", {"form": form})
    
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

    def get_success_url(self) -> str:
        return str(reverse_lazy("chamados:detalhe", kwargs={"pk": self.kwargs["chamado_pk"]}))

class ItemChamadoUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemChamado
    form_class = ItemChamadoForm
    template_name = "chamados/item_form.html"

    def get_success_url(self) -> str:
        return str(reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk}))

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

    def get_success_url(self) -> str:  # type: ignore[override]
        return str(reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk}))

class IndexPageView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "chamados/index.html"
    context_object_name = "chamados"

    def get_queryset(self):
        return Chamado.objects.select_related("tecnico", "usuario").prefetch_related("itens")[:10]  # type: ignore[attr-defined]

class CadastroPageView(ChamadoCreateView):
    """Mesma lógica de criação, rota alternativa para o formulário de cadastro."""
    pass

class ChamadosAtribuidosView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "chamados/atribuidos.html"
    context_object_name = "chamados"

    def get_queryset(self):
        return Chamado.objects.filter(tecnico=self.request.user).select_related('usuario')  # type: ignore[attr-defined]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chamados_abertos_count"] = self.get_queryset().filter(status__in=['AB', 'EA']).count()
        context["status_choices"] = Chamado.Status.choices
        # Pega o primeiro item com estoque baixo para o alerta
        context["estoque_baixo"] = ItemEstoque.objects.filter(quantidade__lte=models.F('quantidade_minima')).first()  # type: ignore[attr-defined]
        return context
    
from django.contrib.auth import get_user_model
User = get_user_model()

class ReatribuicaoTecnicoView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "estoque/reatribuir_tecnico.html" 
    context_object_name = "chamados"

    def get_queryset(self):
        qs = Chamado.objects.filter(status__in=['AB', 'EA']).select_related('tecnico', 'usuario')
    
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
    
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(numero_protocolo__icontains=q) |
                Q(tecnico__first_name__icontains=q) |
                Q(tecnico__last_name__icontains=q)
            )
    
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tecnicos"] = User.objects.filter(is_active=True)  # type: ignore[attr-defined]
        # Busca as últimas 10 reatribuições para o histórico
        context["historico"] = AlteracaoChamado.objects.filter(  # type: ignore[attr-defined]
            descricao__icontains="Reatribuído"
        ).select_related('chamado', 'usuario')[:10]
        return context

    def post(self, request, *args, **kwargs):
        chamado_id = request.POST.get("chamado_id")
        tecnico_id = request.POST.get("tecnico_id")
        
        chamado = get_object_or_404(Chamado, id=chamado_id)
        novo_tecnico = get_object_or_404(User, id=tecnico_id)
        
        tecnico_anterior = chamado.tecnico
        chamado.tecnico = novo_tecnico
        chamado.save()
        
        nome_anterior = tecnico_anterior.first_name if tecnico_anterior else 'Ninguém'
        AlteracaoChamado.objects.create(  # type: ignore[attr-defined]
            chamado=chamado,
            status_anterior=chamado.status,
            status_novo=chamado.status,
            descricao=f"Reatribuído: de {nome_anterior} para {novo_tecnico.first_name}",
            usuario=request.user
        )
        
        messages.success(request, f"Chamado {chamado.numero_protocolo} reatribuído com sucesso.")
        return redirect("chamados:reatribuir_tecnico")

# Made with Bob
