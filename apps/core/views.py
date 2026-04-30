from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.urls import reverse_lazy

from apps.core.forms import UserForm

from django.contrib.auth import get_user_model

User = get_user_model()

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "core/lista.html"
    context_object_name = "usuarios"
    
class UserLoginView(View):
    def get(self, request):
        return render(request, "core/login.html")

    def post(self, request):
        matricula = request.POST.get("matricula")
        password = request.POST.get("password")

        user = authenticate(request, matricula=matricula, password=password)

        if user is not None:
            login(request, user)
            return redirect("estoque:lista")

        return render(request, "core/login.html", {
            "erro": "Credenciais inválidas"
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