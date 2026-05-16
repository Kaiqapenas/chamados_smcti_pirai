from django.urls import path
from .views import (
    UserListView, UserCreateView, UserDetailView,
    UserLoginView, UserLogoutView, UserUpdateView, UserDeleteView,
   RecuperarSenhaView, EmailEnviadoView, NovaSenhaView, RegistroAutoriaView, RegistroAutoriaKPIView,
    RegistroAutoriaListAPIView, RegistroAutoriaExportCSVView,
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
    path("registro-autoria/", RegistroAutoriaView.as_view(), name="registro_autoria"),
    path("api/registro-autoria/kpi/",    RegistroAutoriaKPIView.as_view(),    name="registro_autoria_kpi"),
    path("api/registro-autoria/lista/",  RegistroAutoriaListAPIView.as_view(), name="registro_autoria_lista"),
    path("api/registro-autoria/export/", RegistroAutoriaExportCSVView.as_view(), name="registro_autoria_export"),
]

    #path("administracao-funcionarios/", AdminFuncionariosView.as_view(), name="admin_funcionarios")

    # Recuperação de senha

    path("recuperar-senha/", RecuperarSenhaView.as_view(), name="recuperar_senha"),
    path("email-enviado/",   EmailEnviadoView.as_view(),   name="email_enviado"),
    path("nova-senha/",      NovaSenhaView.as_view(),      name="nova_senha"),
]