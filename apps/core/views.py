import csv
import json
from functools import reduce
from operator import or_

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator

from apps.core.forms import UserForm
from apps.core.models import AuditoriaLog, TipoEvento
from apps.core.mixins import AdministradorRequiredMixin, AdministradorOuSecretarioRequiredMixin

from django.contrib.auth import get_user_model

User = get_user_model()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# CRUD DE USUARIOS:

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "core/lista.html"
    context_object_name = "usuarios"


class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("chamados:lista")
        return render(request, "auth/login.html")

    def post(self, request):
        matricula = request.POST.get("matricula", "").strip()
        password = request.POST.get("password", "")
        ip = get_client_ip(request)

        user = authenticate(request, username=matricula, password=password)

        if user is not None:
            if not user.ativo:
                return render(request, "auth/login.html", {
                    "erro": "Usuário inativo. Contate o administrador."
                })
            login(request, user)
            AuditoriaLog.objects.create(
                tipo=TipoEvento.LOGIN,
                usuario=user,
                descricao=f"Login realizado pela matrícula {user.matricula}.",
                ip=ip,
            )
            next_url = request.GET.get("next") or "chamados:lista"
            return redirect(next_url)

        AuditoriaLog.objects.create(
            tipo=TipoEvento.LOGIN_FALHA,
            usuario=None,
            matricula_tentativa=matricula,
            descricao=f"Tentativa de login falha para a matrícula {matricula}.",
            ip=ip,
        )
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

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditoriaLog.objects.create(
            tipo=TipoEvento.EDICAO,
            usuario=self.request.user,
            descricao=f"Usuário {self.object.matricula} editado por {self.request.user.matricula}.",
            ip=get_client_ip(self.request),
        )
        return response


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = "core/confirma_exclusao.html"
    success_url = reverse_lazy("core:index")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        matricula = self.object.matricula
        response = super().post(request, *args, **kwargs)
        AuditoriaLog.objects.create(
            tipo=TipoEvento.EXCLUSAO,
            usuario=request.user,
            descricao=f"Usuário {matricula} excluído por {request.user.matricula}.",
            ip=get_client_ip(request),
        )
        return response


class AdminFuncionariosView(AdministradorRequiredMixin, LoginRequiredMixin, View):
    # View para gerenciamento de funcionarios - requer permsisao de administrador
    def get(self, request):
        usuarios = []
        for u in User.objects.all().order_by('first_name', 'last_name'):
            perfis = []
            if u.is_administrador: perfis.append('Administrativo')
            if u.is_tecnico:       perfis.append('Técnico')
            if u.is_almoxarife:    perfis.append('Almoxarife')
            if u.is_solicitante:   perfis.append('Solicitante')
            if u.is_secretario:    perfis.append('Secretário')
            usuarios.append({
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'matricula': u.matricula,
                'email': u.email or '',
                'telefone': u.telefone or '',
                'setor': u.setor or '',
                'ativo': u.ativo,
                'perfis': perfis,
            })
        return render(request, "admin/administracao_funcionarios.html", {
            "funcionarios_json": json.dumps(usuarios)
        })

    def post(self, request):
        data = json.loads(request.body)
        
        # Verifica se é uma requisição de exclusão
        if data.get('action') == 'inativar':
            user_id = data.get('id')
            try:
                user = User.objects.get(id=user_id)
                # Não permite deletar o próprio usuário
                if user.id == request.user.id:
                    return JsonResponse({'erro': 'Você não pode inativar seu próprio usuário.'}, status=400)
                user.ativo = False
                user.save()
                # Registra a exclusão no log de auditoria
                AuditoriaLog.objects.create(
                    tipo=TipoEvento.EXCLUSAO,
                    usuario=request.user,
                    descricao=f"Usuário {user.matricula} ({user.first_name} {user.last_name}) foi excluído.",
                    ip=get_client_ip(request),
                )

                return JsonResponse({'ok': True})
            except User.DoesNotExist:
                return JsonResponse({'erro': 'Usuário não encontrado.'}, status=404)
        #reativar
        if data.get('action') == 'reativar':
            user_id = data.get('id')
            try:
                user = User.objects.get(id=user_id)
                user.ativo = True
                user.save()
                AuditoriaLog.objects.create(
                    tipo=TipoEvento.EDICAO,
                    usuario=request.user,
                    descricao=f"Usuário {user.matricula} ({user.first_name} {user.last_name}) foi reativado.",
                    ip=get_client_ip(request),
                )
                return JsonResponse({'ok':True})
            except User.DoesNotExist:
                return JsonResponse({'erro': 'Usuário não encontrado.'}, status=404)

        #editar
        if data.get('action') == 'editar':
            user_id = data.get('id')
            try:
                user = User.objects.get(id=user_id)

                # Verifica duplicatas de matrícula e email (excluindo o próprio usuário)
                nova_matricula = data.get('matricula', '').strip()
                novo_email = data.get('email', '').strip()

                if User.objects.filter(matricula=nova_matricula).exclude(id=user_id).exists():
                    return JsonResponse({'erro': 'Matrícula já cadastrada.'}, status=400)
                if User.objects.filter(email=novo_email).exclude(id=user_id).exists():
                    return JsonResponse({'erro': 'E-mail já cadastrado.'}, status=400)

                nomes = data.get('nome', '').strip().split(' ', 1)
                setor = data.get('setor', '')

                user.first_name = nomes[0]
                user.last_name = nomes[1] if len(nomes) > 1 else ''
                user.matricula = nova_matricula
                user.email = novo_email
                user.telefone = data.get('telefone', '')
                user.setor = setor

                perfis = data.get('perfis', [])
                user.is_administrador = 'Administrativo' in perfis
                user.is_tecnico       = 'Técnico'        in perfis
                user.is_almoxarife    = 'Almoxarife'     in perfis
                user.is_solicitante   = 'Solicitante'    in perfis
                user.is_secretario    = 'Secretário'     in perfis

                user.save()
                AuditoriaLog.objects.create(
                    tipo=TipoEvento.EDICAO,
                    usuario=request.user,
                    descricao=f"Usuário {user.matricula} ({user.first_name} {user.last_name}) editado por {request.user.matricula}.",
                    ip=get_client_ip(request),
                )
                return JsonResponse({'ok': True})
            except User.DoesNotExist:
                return JsonResponse({'erro': 'Usuário não encontrado.'}, status=404)        

        # Criação de novo usuário
        if User.objects.filter(matricula=data.get('matricula')).exists():
            return JsonResponse({'erro': 'Matrícula já cadastrada.'}, status=400)

        if User.objects.filter(email=data.get('email')).exists():
            return JsonResponse({'erro': 'E-mail já cadastrado.'}, status=400)

        nomes = data.get('nome', '').strip().split(' ', 1)
        setor = data.get('setor', '')
        
        user = User.objects.create_user(
            matricula=data.get('matricula'),
            password=data.get('senha'),
            first_name=nomes[0],
            last_name=nomes[1] if len(nomes) > 1 else '',
            email=data.get('email', ''),
            telefone=data.get('telefone', ''),
            setor=setor,
            is_active=True,
        )
        
        # Atribui as permissões baseadas no setor
        # ── Criação — substitui o bloco de permissões ──
        user.is_administrador = 'Administrativo' in data.get('perfis', [])
        user.is_tecnico       = 'Técnico'        in data.get('perfis', [])
        user.is_almoxarife    = 'Almoxarife'     in data.get('perfis', [])
        user.is_solicitante   = 'Solicitante'    in data.get('perfis', [])
        user.is_secretario    = 'Secretário'     in data.get('perfis', [])
        user.save()

        # Registra a criação no log de auditoria
        AuditoriaLog.objects.create(
            tipo=TipoEvento.CRIACAO,
            usuario=request.user,
            descricao=f"Novo usuário criado: {user.matricula} ({user.first_name} {user.last_name}) - Setor: {setor}",
            ip=get_client_ip(request),
        )
        
        return JsonResponse({'ok': True, 'id': user.id})


class RegistroauditoriaView(AdministradorOuSecretarioRequiredMixin, LoginRequiredMixin, View):
    """View para visualização de registros de auditoria - requer permissão de administrador"""

    def get(self, request):
        return render(request, "admin/registro_auditoria.html")


class RegistroauditoriaKPIView(AdministradorOuSecretarioRequiredMixin, LoginRequiredMixin, View):
    """View para KPIs de auditoria - requer permissão de administrador"""

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


# auth de senha

class AlterarSenhaView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "auth/alterar_senha.html")

    def post(self, request):
        senha_atual = request.POST.get("senha_atual", "")
        senha1 = request.POST.get("password1", "")
        senha2 = request.POST.get("password2", "")

        if not request.user.check_password(senha_atual):
            return render(request, "auth/alterar_senha.html", {
                "erro": "Senha atual incorreta."
            })

        if not senha1 or senha1 != senha2:
            return render(request, "auth/alterar_senha.html", {
                "erro": "As novas senhas não coincidem ou estão vazias."
            })

        if len(senha1) < 6:
            return render(request, "auth/alterar_senha.html", {
                "erro": "A nova senha deve ter pelo menos 6 caracteres."
            })

        request.user.set_password(senha1)
        request.user.save()

        # Mantém o usuário logado após trocar a senha
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)

        return render(request, "auth/alterar_senha.html", {"sucesso": True})
        
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
            return render(request, "auth/recuperar_senha.html", {
                "erro": "Informe um e-mail válido."
            })

        # Resposta sempre igual pra não revelar se o e-mail existe
        user = User.objects.filter(email=email, ativo=True).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = request.build_absolute_uri(
                reverse_lazy("core:nova_senha", kwargs={"uidb64": uid, "token": token})
            )
            send_mail(
                subject="Redefinição de senha — SIGEC",
                message=f"Olá, {user.first_name}.\n\nClique no link abaixo para redefinir sua senha:\n\n{link}\n\nSe não foi você, ignore este e-mail.",
                from_email=None,  # usa DEFAULT_FROM_EMAIL do settings
                recipient_list=[email],
            )

        request.session["recuperacao_email"] = email
        return redirect("core:email_enviado")


class EmailEnviadoView(View):
    """Tela de confirmação exibida após solicitar recuperação de senha."""

    def get(self, request):
        # Recupera o e-mail salvo na sessão (pode estar vazio se acessado direto)
        email = request.session.pop(
            "recuperacao_email", "seu e-mail cadastrado")
        return render(request, "auth/email_enviado.html", {"email": email})


class NovaSenhaView(View):
    """
    Tela de redefinição de senha.
    Sem token real por enquanto — o fluxo completo depende do envio de e-mail.
    Quando estiver pronto: validar token via PasswordResetConfirmView ou implementação própria,
    identificar o usuário e chamar user.set_password(senha).
    """

    def get(self, request, uidb64=None, token=None):
        user = self._validar_token(uidb64, token)
        if not user:
            return render(request, "auth/nova_senha.html", {"erro": "Link inválido ou expirado. Solicite uma nova recuperação de senha."})
        return render(request, "auth/nova_senha.html", {"validacao_ok": True})

    def post(self, request, uidb64=None, token=None):
        user = self._validar_token(uidb64, token)
        if not user:
            return render(request, "auth/nova_senha.html", {
                "erro": "Link inválido ou expirado. Solicite uma nova recuperação de senha."
            })

        senha1 = request.POST.get("password1", "")
        senha2 = request.POST.get("password2", "")

        if not senha1 or senha1 != senha2:
            return render(request, "auth/nova_senha.html", {
                "erro": "As senhas não coincidem ou estão vazias.",
                "uidb64": uidb64,
                "token": token,
            })

        if len(senha1) < 6:
            return render(request, "auth/nova_senha.html", {
                "erro": "A senha deve ter pelo menos 6 caracteres.",
                "uidb64": uidb64,
                "token": token,
            })

        user.set_password(senha1)
        user.save()
        return render(request, "auth/nova_senha.html", {"sucesso": True})

    def _validar_token(self, uidb64, token):
        if not uidb64 or not token:
            return None
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid, ativo=True)
        except (User.DoesNotExist, ValueError, TypeError):
            return None
        if not default_token_generator.check_token(user, token):
            return None
        return user


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
    'modificacao': [TipoEvento.EDICAO, TipoEvento.CRIACAO, TipoEvento.EXCLUSAO],
    'negado':     [TipoEvento.LOGIN_FALHA],
}


def _build_log_queryset(request):
    """Retorna queryset de AuditoriaLog aplicando busca e filtro da request."""
    qs = AuditoriaLog.objects.select_related('usuario').all()

    q = request.GET.get('q', '').strip()
    if q:
        q_objects = [
            Q(descricao__icontains=q),
            Q(ip__icontains=q),
            Q(usuario__matricula__icontains=q),
            Q(matricula_tentativa__icontains=q)
        ]
        query = reduce(or_, q_objects)
        qs = qs.filter(query)

    tipo_filtro = request.GET.get('tipo', '').strip()
    if tipo_filtro in FILTRO_TIPO_MAP:
        qs = qs.filter(tipo__in=FILTRO_TIPO_MAP[tipo_filtro])

    return qs


def _serialize_log(log):
    """Serializa um AuditoriaLog para dicionário JSON."""
    local_dt = timezone.localtime(log.data)
    ator = log.usuario.matricula if log.usuario else (
        log.matricula_tentativa or 'Desconhecido')
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
        page_obj = paginator.get_page(page_num)

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
        writer.writerow(['ID', 'Tipo', 'Evento', 'Nome',
                        'Matrícula/Ator', 'IP', 'Descrição', 'Data', 'Hora'])

        for log in qs:
            local_dt = timezone.localtime(log.data)
            ator = log.usuario.matricula if log.usuario else (
                log.matricula_tentativa or 'Desconhecido')
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

