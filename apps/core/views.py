import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

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


# ─── Audit Log helpers ────────────────────────────────────────────────────────

TIPO_COR_MAP = {
    TipoEvento.LOGIN:       'blue',
    TipoEvento.LOGIN_FALHA: 'red',
    TipoEvento.LOGOUT:      'yellow',
    TipoEvento.ACESSO:      'blue',
    TipoEvento.CRIACAO:     'green',
    TipoEvento.EDICAO:      'yellow',
    TipoEvento.EXCLUSAO:    'red',
}

FILTRO_TIPO_MAP = {
    'login':      [TipoEvento.LOGIN, TipoEvento.LOGOUT, TipoEvento.ACESSO],
    'modificacao':[TipoEvento.EDICAO, TipoEvento.CRIACAO, TipoEvento.EXCLUSAO],
    'negado':     [TipoEvento.LOGIN_FALHA],
}


def _build_log_queryset(request):
    """Retorna queryset de AuditoriaLog aplicando busca e filtro da request."""
    qs = AuditoriaLog.objects.select_related('usuario').all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(descricao__icontains=q) |
            Q(ip__icontains=q) |
            Q(usuario__matricula__icontains=q) |
            Q(matricula_tentativa__icontains=q)
        )

    tipo_filtro = request.GET.get('tipo', '').strip()
    if tipo_filtro in FILTRO_TIPO_MAP:
        qs = qs.filter(tipo__in=FILTRO_TIPO_MAP[tipo_filtro])

    return qs


def _serialize_log(log):
    """Serializa um AuditoriaLog para dicionário JSON."""
    local_dt = timezone.localtime(log.data)
    ator = log.usuario.matricula if log.usuario else (log.matricula_tentativa or 'Desconhecido')
    nome = ''
    if log.usuario:
        nome = f"{log.usuario.first_name} {log.usuario.last_name}".strip()
    return {
        'id':        log.id,
        'tipo':      log.tipo,
        'titulo':    log.get_tipo_display(),
        'subtitulo': log.descricao,
        'usuario':   ator,
        'nome':      nome,
        'ip':        log.ip or '',
        'data':      local_dt.strftime('%d/%m'),
        'hora':      local_dt.strftime('%H:%M'),
        'cor':       TIPO_COR_MAP.get(log.tipo, 'blue'),
    }


# ─── Lista paginada ───────────────────────────────────────────────────────────

class RegistroAutoriaListAPIView(View):
    PAGE_SIZE = 15

    def get(self, request):
        qs = _build_log_queryset(request)
        page_num = max(1, int(request.GET.get('page', 1) or 1))
        paginator = Paginator(qs, self.PAGE_SIZE)
        page_obj  = paginator.get_page(page_num)

        return JsonResponse({
            'results':      [_serialize_log(log) for log in page_obj.object_list],
            'page':         page_obj.number,
            'total_pages':  paginator.num_pages,
            'total_count':  paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next':     page_obj.has_next(),
        })


# ─── Exportação CSV ───────────────────────────────────────────────────────────

class RegistroAutoriaExportCSVView(View):
    def get(self, request):
        qs = _build_log_queryset(request)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="auditoria_logs.csv"'
        response.write('\ufeff')  # BOM para compatibilidade com Excel

        writer = csv.writer(response)
        writer.writerow(['ID', 'Tipo', 'Evento', 'Nome', 'Matrícula/Ator', 'IP', 'Descrição', 'Data', 'Hora'])

        for log in qs:
            local_dt = timezone.localtime(log.data)
            ator = log.usuario.matricula if log.usuario else (log.matricula_tentativa or 'Desconhecido')
            nome = ''
            if log.usuario:
                nome = f"{log.usuario.first_name} {log.usuario.last_name}".strip()
            writer.writerow([
                log.id,
                log.tipo,
                log.get_tipo_display(),
                nome,
                ator,
                log.ip or '',
                log.descricao,
                local_dt.strftime('%d/%m/%Y'),
                local_dt.strftime('%H:%M'),
            ])

        return response
