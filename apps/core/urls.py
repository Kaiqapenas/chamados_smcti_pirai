from django.urls import path
from .views import (
    UserListView, UserCreateView, UserDetailView,
    UserLoginView, UserLogoutView, UserUpdateView, UserDeleteView,
   RecuperarSenhaView, EmailEnviadoView, NovaSenhaView, RegistroauditoriaView, RegistroauditoriaKPIView,
    RegistroauditoriaListAPIView, RegistroauditoriaExportCSVView,
)

app_name = "core"

urlpatterns = [
    path("", UserListView.as_view(), name="index"),
    path("adicionar/", UserCreateView.as_view(), name="adicionar"),
    path("<int:pk>/", UserDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", UserUpdateView.as_view(), name="editar"),
    path("<int:pk>/remover/", UserDeleteView.as_view(), name="excluir"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("sair/", UserLogoutView.as_view(), name="sair"),
    path("administracao-funcionarios/", AdminFuncionariosView.as_view(), name="admin_funcionarios"),
    path("registro-auditoria/", RegistroauditoriaView.as_view(), name="registro_auditoria"),
    path("api/registro-auditoria/kpi/",    RegistroauditoriaKPIView.as_view(),    name="registro_auditoria_kpi"),
    path("api/registro-auditoria/lista/",  RegistroauditoriaListAPIView.as_view(), name="registro_auditoria_lista"),
    path("api/registro-auditoria/export/", RegistroauditoriaExportCSVView.as_view(), name="registro_auditoria_export"),
]

    #path("administracao-funcionarios/", AdminFuncionariosView.as_view(), name="admin_funcionarios")

    # Recuperação de senha

    path("recuperar-senha/", RecuperarSenhaView.as_view(), name="recuperar_senha"),
    path("email-enviado/",   EmailEnviadoView.as_view(),   name="email_enviado"),
    path("nova-senha/",      NovaSenhaView.as_view(),      name="nova_senha"),
]