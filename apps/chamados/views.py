from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError

from apps.chamados.forms import ChamadoForm
# from apps.core.views import User
from .models import Chamado, AlteracaoChamado, ItemChamado
from .forms import ItemChamadoForm

from apps.estoque.models import ItemEstoque
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ChamadoListView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "chamados/index.html"
    context_object_name = "chamados"
    ordering = ["-id"]

    def get_queryset(self):

        queryset = (
            super()
            .get_queryset()
            .prefetch_related("itens")
        )

        # =========================
        # FILTRO STATUS
        # =========================

        status = self.request.GET.get("status")

        if status and status != "all":
            queryset = queryset.filter(status=status)

        # =========================
        # FILTRO URGÊNCIA
        # =========================

        urgencia = self.request.GET.get("urgencia")

        if urgencia and urgencia != "all":
            queryset = queryset.filter(urgencia=urgencia)

        # =========================
        # BUSCA PROTOCOLO
        # =========================

        protocolo = self.request.GET.get("protocolo")

        if protocolo:
            queryset = queryset.filter(
                numero_protocolo__icontains=protocolo
            )

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # opções dos filtros
        context["status_choices"] = Chamado.Status.choices
        context["urgencia_choices"] = Chamado.Urgencia.choices

        # valores atuais selecionados
        context["status_atual"] = self.request.GET.get("status", "")
        context["urgencia_atual"] = self.request.GET.get("urgencia", "")
        context["protocolo_atual"] = self.request.GET.get("protocolo", "")

        return context
        
class ChamadoCreateView(LoginRequiredMixin, View):
    def get(self, request):

        form = ChamadoForm()

        usuarios = User.objects.all().order_by("first_name")
                
        return render(
            request,
            "chamados/form.html",
            {
                "form": form,
                "usuarios": usuarios,
                "modo_edicao": False,
            }
        )

    def post(self, request):
        # DEBUG: Imprime os dados recebidos do formulário para verificar o que está chegando
        print(request.POST)
        
        form = ChamadoForm(request.POST)

        # DEBUG: Imprime se o formulário é válido e os erros caso não seja
        print(form.is_valid())
        
        #DEBUG: Imprime os erros do formulário para entender o que está falhando na validação
        print(form.errors)
        
        if form.is_valid():

            chamado = form.save(commit=False)

            chamado.usuario = request.user

            chamado.save()

            messages.success(
                request,
                "Chamado criado com sucesso."
            )

            return redirect(
                "chamados:detalhe",
                pk=chamado.pk
            )

        return render(
            request,
            "chamados/form.html",
            {
                "form": form,
                "modo_edicao": False,
            }
        )

class ChamadoDetailView(LoginRequiredMixin, DetailView):
    model = Chamado
    template_name = "chamados/detalhe.html"
    context_object_name = "chamado"
    
class ChamadoUpdateView(LoginRequiredMixin, View):
    
    def get(self, request, pk):

        chamado = get_object_or_404(
            Chamado,
            pk=pk
        )
        
        usuarios = User.objects.all().order_by("first_name")

        if chamado.status == Chamado.Status.FINALIZADO:

            messages.error(
                request,
                "Não é possível editar um chamado finalizado."
            )

            return redirect(
                "chamados:detalhe",
                pk=pk
            )

        form = ChamadoForm(instance=chamado)

        return render(
            request,
            "chamados/form.html",
            {
                "form": form,
                "chamado": chamado,
                "usuarios": usuarios,
                "modo_edicao": True,
            }
        )

    def post(self, request, pk):

        chamado = get_object_or_404(
            Chamado,
            pk=pk
        )

        if chamado.status == Chamado.Status.FINALIZADO:

            messages.error(
                request,
                "Não é possível editar um chamado finalizado."
            )

            return redirect(
                "chamados:detalhe",
                pk=pk
            )

        form = ChamadoForm(
            request.POST,
            instance=chamado
        )

        if form.is_valid():

            chamado = form.save(commit=False)

            chamado.usuario = request.user

            chamado.save()

            messages.success(
                request,
                "Chamado atualizado com sucesso."
            )

            return redirect(
                "chamados:detalhe",
                pk=pk
            )

        return render(
            request,
            "chamados/form.html",
            {
                "form": form,
                "chamado": chamado,
                "modo_edicao": True,
            }
        )

class ChamadoDeleteView(LoginRequiredMixin, View):
    model = Chamado
    def post(self, request, pk):
        chamado = get_object_or_404(Chamado, pk=pk)
        chamado.delete()
        return redirect("chamados:index")

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


class ChamadosAtribuidosView(LoginRequiredMixin, ListView):
    model = Chamado
    template_name = "chamados/atribuidos.html"
    context_object_name = "chamados"

    def get_queryset(self):
        return Chamado.objects.filter(tecnico=self.request.user).select_related('usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chamados_abertos_count"] = self.get_queryset().filter(status__in=['AB', 'EA']).count()
        context["status_choices"] = Chamado.Status.choices
        # Pega o primeiro item com estoque baixo para o alerta
        context["estoque_baixo"] = ItemEstoque.objects.filter(quantidade__lte=models.F('quantidade_minima')).first()
        return context