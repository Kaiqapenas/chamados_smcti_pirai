from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('grafico/', views.RelatorioGraficoView.as_view(), name='grafico'),
]

