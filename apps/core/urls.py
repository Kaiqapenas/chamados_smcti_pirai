from django.urls import path
from .views import (
    UserListView, UserCreateView, UserDetailView,
    UserLoginView, UserLogoutView, UserUpdateView, UserDeleteView,
    AdminFuncionariosView, RegistroAutoriaView, RegistroAutoriaKPIView,
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
