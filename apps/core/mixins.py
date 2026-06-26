from typing import Any
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

class AuthenticatedHttpRequest(HttpRequest):
    user: AbstractBaseUser | AnonymousUser


class AdministradorRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja administrador"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]

    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_administrador

    def handle_no_permission(self) -> HttpResponseRedirect:
        if not self.request.user.is_authenticated:
            return redirect('core:login')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)
        messages.error(self.request, "Acesso restrito a administradores.")
        return redirect('chamados:index')
class AdministradorOuSecretarioRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja administrador ou secretário"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and (
            self.request.user.is_administrador or self.request.user.is_secretario
        )
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        if not self.request.user.is_authenticated:
            return redirect('core:login')
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)
        messages.error(self.request, "Acesso restrito a administradores e secretários.")
        return redirect('chamados:index')

class TecnicoRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja técnico"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_tecnico
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas administradores.")
        return redirect('chamados:index')


class AlmoxarifeRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja almoxarife"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_almoxarife
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas almoxarifes.")
        return redirect('chamados:index')  # type: ignore[return-value]


class SecretarioRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja secretário"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_secretario
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas secretários.")
        return redirect('chamados:index')  # type: ignore[return-value]


class SolicitanteRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja solicitante"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_solicitante
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas solicitantes.")
        return redirect('chamados:index')  # type: ignore[return-value]

# Made with Bob
