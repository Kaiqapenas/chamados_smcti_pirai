from typing import Any
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponseRedirect

# Type stub for request with user attribute
if False:  # TYPE_CHECKING equivalent
    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
    
    class AuthenticatedHttpRequest(HttpRequest):
        user: AbstractBaseUser | AnonymousUser


class AdministradorRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja administrador"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_administrador
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas administradores.")
        return redirect('estoque:lista')  # type: ignore[return-value]


class TecnicoRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja técnico"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_tecnico
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas técnicos.")
        return redirect('estoque:lista')  # type: ignore[return-value]


class AlmoxarifeRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja almoxarife"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_almoxarife
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas almoxarifes.")
        return redirect('estoque:lista')  # type: ignore[return-value]


class SecretarioRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja secretário"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_secretario
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas secretários.")
        return redirect('estoque:lista')  # type: ignore[return-value]


class SolicitanteRequiredMixin(UserPassesTestMixin):
    """Mixin que requer que o usuário seja solicitante"""
    request: AuthenticatedHttpRequest  # type: ignore[assignment]
    
    def test_func(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.is_solicitante
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        messages.error(self.request, "Você não tem permissão para acessar esta página. Apenas solicitantes.")
        return redirect('estoque:lista')  # type: ignore[return-value]

# Made with Bob
