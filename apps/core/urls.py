from django.urls import path
from .views import UserListView, UserCreateView, UserDetailView, UserLoginView, UserLogoutView, UserUpdateView, UserDeleteView
from django.contrib.auth.views import LogoutView

app_name = "core"

urlpatterns = [
    path("", UserListView.as_view(), name="index"),
    path("adicionar/", UserCreateView.as_view(), name="adicionar"),
    path("<int:pk>/", UserDetailView.as_view(), name="detalhe"),
    path("<int:pk>/editar/", UserUpdateView.as_view(), name="editar"),
    path("<int:pk>/remover/", UserDeleteView.as_view(), name="excluir"),
    path("login/", UserLoginView.as_view(), name="login"),  # Placeholder para login 
    path("sair/", UserLogoutView.as_view(), name="sair")
]