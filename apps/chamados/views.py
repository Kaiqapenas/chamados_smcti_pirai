from typing import TYPE_CHECKING, Any, cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.chamados.forms import ChamadoForm
from .models import Chamado, AlteracaoChamado, ItemChamado
from .forms import ItemChamadoForm, ItemChamadoFormSet

from apps.core.models import AuditoriaLog, TipoEvento
from apps.estoque.models import ItemEstoque
from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from django.db.models.manager import Manager

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

class ChamadoListView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "chamados/lista.html"
    context_object_name = "chamados"
 
    def _perfis(self, user):
        return {
            'admin':       getattr(user, 'is_administrador', False),
            'secretario':  getattr(user, 'is_secretario', False),
            'tecnico':     getattr(user, 'is_tecnico', False),
            'solicitante': getattr(user, 'is_solicitante', False),
            'almoxarife':  getattr(user, 'is_almoxarife', False),
        }
 
    def get(self, request, *args, **kwargs):
        p = self._perfis(request.user)
 
        # Almoxarife puro → sem acesso a chamados
        if p['almoxarife'] and not any([p['admin'], p['tecnico'], p['solicitante'], p['secretario']]):
            messages.error(request, "Você não tem acesso a chamados.")
            return redirect("estoque:lista")
 
        # Secretário puro → sem acesso a chamados
        if p['secretario'] and not any([p['admin'], p['tecnico'], p['solicitante'], p['almoxarife']]):
            messages.error(request, "Você não tem acesso a chamados.")
            return redirect("relatorios:relatorio_grafico")
 
        # Técnico puro → vai direto pra atribuídos
        if p['tecnico'] and not any([p['admin'], p['solicitante'], p['secretario'], p['almoxarife']]):
            return redirect("chamados:atribuidos")
 
        return super().get(request, *args, **kwargs)
 
    def get_queryset(self):
        p = self._perfis(self.request.user)
        queryset = super().get_queryset().select_related().prefetch_related("itens")
 
        if p['admin']:
            # Admin vê tudo
            pass
        elif p['solicitante'] and p['tecnico']:
            # Misto solicitante+técnico → os próprios + atribuídos
            queryset = queryset.filter(
                Q(usuario=self.request.user) | Q(tecnico=self.request.user)
            ).distinct()
        elif p['solicitante']:
            # Solicitante puro → só os próprios
            queryset = queryset.filter(usuario=self.request.user)
        elif p['tecnico']:
            # Técnico com outro perfil (ex: técnico+almoxarife) → só atribuídos
            queryset = queryset.filter(tecnico=self.request.user)
 
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
 
        urgencia = self.request.GET.get("urgencia")
        if urgencia:
            queryset = queryset.filter(urgencia=urgencia)
 
        protocolo = self.request.GET.get("protocolo")
        if protocolo:
            queryset = queryset.filter(numero_protocolo__icontains=protocolo)
 
        tecnico_id = self.request.GET.get("tecnico")
        if tecnico_id:
            queryset = queryset.filter(tecnico__id=tecnico_id)
 
        periodo = self.request.GET.get("periodo")
        if periodo:
            hoje = timezone.now()
            if periodo == "diario":
                queryset = queryset.filter(data_criacao__date=hoje.date())
            elif periodo == "mensal":
                queryset = queryset.filter(
                    data_criacao__year=hoje.year,
                    data_criacao__month=hoje.month
                )
            elif periodo == "anual":
                queryset = queryset.filter(data_criacao__year=hoje.year)
 
        return queryset
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Chamado.Status.choices
        context["urgencia_choices"] = Chamado.Urgencia.choices
        context["tecnicos"] = User.objects.filter(is_tecnico=True, ativo=True)
        return context   
        
class ChamadoCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ChamadoForm()
        return render(request, "chamados/cadastro.html", {"form": form, "form_mode": "create"})

    def post(self, request):
        form = ChamadoForm(request.POST, request.FILES)

        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.usuario = request.user
            chamado.save()
            AuditoriaLog.objects.create(
                tipo=TipoEvento.CRIACAO,
                usuario=request.user,
                descricao=f"Chamado {chamado.numero_protocolo} criado",
                ip=get_client_ip(request)
            )
            messages.success(request, "Chamado criado com sucesso")
            return redirect("chamados:lista")

        return render(request, "chamados/cadastro.html", {"form": form, "form_mode": "create"})
    
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
        return render(request, "chamados/cadastro.html", {"form": form, "chamado": chamado, "form_mode": "update"})

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
            AuditoriaLog.objects.create(
                tipo=TipoEvento.EDICAO,
                usuario=request.user,
                descricao=f"Chamado {chamado.numero_protocolo} editado",
                ip=get_client_ip(request),
            )
            messages.success(request, "Chamado atualizado com sucesso.")
            return redirect("chamados:detalhe", pk=pk)

        return render(request, "chamados/cadastro.html", {"form": form, "chamado": chamado, "form_mode": "update"})

class ChamadoDeleteView(LoginRequiredMixin, View):
    model = Chamado
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        protocolo = chamado.numero_protocolo #salva antes de deletar 
        chamado.delete()
        AuditoriaLog.objects.create(
            tipo=TipoEvento.EXCLUSAO,
            usuario=request.user,
            descricao=f"Chamado {chamado.numero_protocolo} excluído",
            ip=get_client_ip(request),
        )
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
            AuditoriaLog.objects.create(
                tipo=TipoEvento.EDICAO,
                usuario=request.user,
                descricao=f"Status do chamado {chamado.numero_protocolo} alterado para {chamado.get_status_display()}",
                ip=get_client_ip(request),
            )
            messages.success(request, f"Status alterado para {chamado.get_status_display()}")
        except ValidationError as e:
            messages.error(request, str(e))
        return redirect("chamados:detalhe", pk=pk)

#ITENS DO CHAMADO
class ItemChamadoCreateView(LoginRequiredMixin, View):
    template_name = "chamados/item_form.html"

    def _get_chamado(self, chamado_pk):
        chamado = get_object_or_404(Chamado, pk=chamado_pk)
        if chamado.status == Chamado.Status.FINALIZADO:
            messages.error(
                self.request,
                "Não é possível adicionar itens a um chamado finalizado.",
            )
            return None
        return chamado
        
    def form_valid(self, form):
        # Associa o item ao chamado da URL automaticamente
        chamado = get_object_or_404(Chamado, pk = self.kwargs["chamado_pk"])
        form.instance.chamado = chamado
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        AuditoriaLog.objects.create(
            tipo=TipoEvento.CRIACAO,
            usuario=self.request.user,
            descricao=f"Item '{form.instance.nome}' adicionado ao chamado {chamado.numero_protocolo}",
            ip=get_client_ip(self.request),
        )
        return response

    def get(self, request, chamado_pk):
        chamado = self._get_chamado(chamado_pk)
        if chamado is None:
            return redirect("chamados:detalhe", pk=chamado_pk)

        formset = ItemChamadoFormSet(chamado=chamado)
        return render(
            request,
            self.template_name,
            {
                "chamado": chamado,
                "formset": formset,
                "form_mode": "create",
                "existing_item_ids": list(
                    chamado.itens.values_list("item_id", flat=True)
                ),
            },
        )

    def post(self, request, chamado_pk):
        chamado = self._get_chamado(chamado_pk)
        if chamado is None:
            return redirect("chamados:detalhe", pk=chamado_pk)

        formset = ItemChamadoFormSet(request.POST, chamado=chamado)

        if formset.is_valid():
            with transaction.atomic():
                for item_id, quantidade in formset.merged_items.items():
                    ItemChamado.objects.create(
                        chamado=chamado,
                        item_id=item_id,
                        quantidade=quantidade,
                        usuario=request.user,
                    )

            count = len(formset.merged_items)
            messages.success(
                request,
                f"{count} item(ns) adicionado(s) com sucesso.",
            )
            return redirect("chamados:detalhe", pk=chamado_pk)

        return render(
            request,
            self.template_name,
            {
                "chamado": chamado,
                "formset": formset,
                "form_mode": "create",
                "existing_item_ids": list(
                    chamado.itens.values_list("item_id", flat=True)
                ),
            },
        )

class ItemChamadoUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemChamado
    form_class = ItemChamadoForm
    template_name = "chamados/item_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_mode"] = "update"
        context["chamado"] = self.object.chamado
        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.chamado.status == Chamado.Status.FINALIZADO:
            messages.error(
                request,
                "Não é possível editar itens de um chamado finalizado.",
            )
            return redirect("chamados:detalhe", pk=self.object.chamado.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return str(reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk}))

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, "Item atualizado com sucesso.")
        response = super().form_valid(form)
        AuditoriaLog.objects.create(
            tipo=TipoEvento.EDICAO,
            usuario=self.request.user,
            descricao=f"Item do chamado {self.object.chamado.numero_protocolo} editado.",
            ip=get_client_ip(self.request),
        )
        return response

class ItemChamadoDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemChamado
    template_name = "chamados/confirmar_remocao.html"

    def post(self,request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            AuditoriaLog.objects.create(
                tipo=TipoEvento.EXCLUSAO,
                usuario=request.user,
                descricao=f"Item removido do chamado {self.object.chamado.numero_protocolo}.",
                ip=get_client_ip(request),
            )
            messages.success(request, "Item removido com sucesso.")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:  # type: ignore[override]
        return str(reverse_lazy("chamados:detalhe", kwargs={"pk": self.object.chamado.pk}))

from django.views.generic import TemplateView
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
        context["tecnicos"] = User.objects.filter(is_tecnico=True, ativo=True)
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
        AuditoriaLog.objects.create(
            tipo=TipoEvento.EDICAO,
            usuario=request.user,
            descricao=f"Chamado {chamado.numero_protocolo} reatribuído de {nome_anterior} para {novo_tecnico.first_name}.",
            ip=get_client_ip(request),
        )
        
        messages.success(request, f"Chamado {chamado.numero_protocolo} reatribuído com sucesso.")
        return redirect("chamados:reatribuir_tecnico")

# Made with Bob
