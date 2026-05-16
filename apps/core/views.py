import csv

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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


#CRUD DE USUARIOS:

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "core/lista.html"
    context_object_name = "usuarios"


class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("estoque:lista")
        return render(request, "auth/login.html")

    def post(self, request):
        matricula = request.POST.get("matricula", "").strip(, "").strip()
        password = request.POST.get("password", "")
        ip = get_client_ip(request)

        user = authenticate(request, username=matricula, password=password)

        if user is not None:
            if not user.ativo:
                return render(request, "auth/login.html", {
                    "erro": "Usuário inativo. Contate o administrador."
                })
            login(request,user)
            next_url = request.GET.get("next") or "estoque:lista"
            return redirect(next_url)

        return render(request, "auth/login.html", {
            "erro": "Matrícula ou senha inválidas."
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


# class RegistroauditoriaView(LoginRequiredMixin, View):
class RegistroauditoriaView(View):
    def get(self, request):
        return render(request, "admin/registro_auditoria.html")


# class RegistroauditoriaKPIView(LoginRequiredMixin, View):
class RegistroauditoriaKPIView(View):
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


#auth de senha

class RecuperarSenhaView(View):
    """
    simula o envio de e-mail de recuperação.
    não faz nada de verdade, o envio de e-mail será implementado depois.
    a resposta é sempre a mesma para não revelar se a matrícula existe.
    """
    def get(self, request):
        return render(request, "auth/recuperar_senha.html")
    
    def post(self, request):
        email = request.POST.get("email", "").strip()

        if not email or not "@" in email:
            return render(request, "auth/recuperar_senha.html",{
                "erro": "Informe um e-mail válido."
            })
        
        # TODO: quando o backend de e-mail estiver pronto:
        #   1. Buscar User.objects.filter(email=email).first()
        #   2. Gerar token com django.contrib.auth.tokens.default_token_generator
        #   3. Salvar / associar ao usuário
        #   4. Disparar send_mail() com o link contendo o token
        #
        # Por enquanto apenas guardamos o e-mail na sessão pra exibir na tela seguinte.

        request.session["recuperacao_email"] = email
        return redirect("core:email_enviado")

class EmailEnviadoView(View):
    """Tela de confirmação exibida após solicitar recuperação de senha."""
 
    def get(self, request):
        # Recupera o e-mail salvo na sessão (pode estar vazio se acessado direto)
        email = request.session.pop("recuperacao_email", "seu e-mail cadastrado")
        return render(request, "auth/email_enviado.html", {"email": email})

class NovaSenhaView(View):
    """
    Tela de redefinição de senha.
    Sem token real por enquanto — o fluxo completo depende do envio de e-mail.
    Quando estiver pronto: validar token via PasswordResetConfirmView ou implementação própria,
    identificar o usuário e chamar user.set_password(senha).
    """
 
    def get(self, request):
        return render(request, "auth/nova_senha.html")
 
    def post(self, request):
        senha1 = request.POST.get("password1", "")
        senha2 = request.POST.get("password2", "")
 
        if not senha1 or senha1 != senha2:
            return render(request, "auth/nova_senha.html", {
                "erro": "As senhas não coincidem ou estão vazias."
            })
 
        if len(senha1) < 6:
            return render(request, "auth/nova_senha.html", {
                "erro": "A senha deve ter pelo menos 6 caracteres."
            })
 
        # TODO: identificar usuário pelo token e aplicar:
        #   user.set_password(senha1)
        #   user.save()
 
        return render(request, "auth/nova_senha.html", {"sucesso": True})


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

class RegistroauditoriaListAPIView(View):
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

class RegistroauditoriaExportCSVView(View):
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
