from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy

from apps.core.forms import UserForm

from django.contrib.auth import get_user_model

User = get_user_model()

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
        matricula = request.POST.get("matricula", "").strip()
        password = request.POST.get("password", "")

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

# # Create your views here.
# def index(request):
#     return render(request, "base.html")
# Create your views here.

# class AdminFuncionariosView(View): 
#     def get(self, request):
#         return render(request, "admin/administracao_funcionarios.html")
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