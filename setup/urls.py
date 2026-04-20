from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('apps.core.urls')),
    path("chamados/", include("apps.chamados.urls")),
    path("estoque/", include("apps.estoque.urls")),
]
