from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone

from apps.core.forms import UserForm
from apps.core.models import AuditoriaLog, TipoEvento

from django.contrib.auth import get_user_model

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "core/lista.html"
    context_object_name = "usuarios"


class UserLoginView(View):
    def get(self, request):
        return render(request, "core/login.html")

    def post(self, request):
        matricula = request.POST.get("matricula", "").strip()
        password = request.POST.get("password")
        ip = get_client_ip(request)

        user = authenticate(request, matricula=matricula, password=password)

        if user is not None:
            login(request, user)
            AuditoriaLog.objects.create(
                tipo=TipoEvento.LOGIN,
                usuario=user,
                descricao=f"Login bem-sucedido para a matrícula {matricula}.",
                ip=ip,
            )
            return redirect("estoque:lista")

        AuditoriaLog.objects.create(
            tipo=TipoEvento.LOGIN_FALHA,
            usuario=None,
            matricula_tentativa=matricula,
            descricao=f"Tentativa de login falhou para a matrícula '{matricula}'.",
            ip=ip,
        )
        return render(request, "core/login.html", {
            "erro": "Credenciais inválidas"
        })


class UserLogoutView(LoginRequiredMixin, View):
    def post(self, request):
        AuditoriaLog.objects.create(
            tipo=TipoEvento.LOGOUT,
            usuario=request.user,
            descricao=f"Logout da matrícula {request.user.matricula}.",
            ip=get_client_ip(request),
        )
        logout(request)
        return redirect("core:login")


class UserCreateView(LoginRequiredMixin, CreateView):
    form_class = UserForm
    template_name = "core/form.html"
    success_url = reverse_lazy("core:index")


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "core/detalhe.html"
    context_object_name = "usuario"


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "core/form.html"
    success_url = reverse_lazy("core:index")


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "core/confirma_exclusao.html"
    success_url = reverse_lazy("core:index")


class AdminFuncionariosView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "admin/administracao_funcionarios.html")


# class RegistroAutoriaView(LoginRequiredMixin, View):
class RegistroAutoriaView(View):
    def get(self, request):
        return render(request, "admin/registro_autoria.html")


# class RegistroAutoriaKPIView(LoginRequiredMixin, View):
class RegistroAutoriaKPIView(View):
    def get(self, request):
        hoje = timezone.now().date()
        total_eventos = AuditoriaLog.objects.filter(data__date=hoje).count()
        total_logins = AuditoriaLog.objects.filter(
            data__date=hoje, tipo=TipoEvento.LOGIN
        ).count()
        total_falhas = AuditoriaLog.objects.filter(
            data__date=hoje, tipo=TipoEvento.LOGIN_FALHA
        ).count()
        return JsonResponse({
            'eventos_hoje': total_eventos,
            'logins_realizados': total_logins,
            'acessos_negados': total_falhas,
        })


def index(request):
    return render(request, "base.html")
