from django.urls import path
from . import views

urlpatterns = [
    path('', views.RelatorioView.as_view(), name='relatorio_view'),
    path('get_relatorio', views.GetRelatorioView.as_view(), name='get_relatorio'),
]
