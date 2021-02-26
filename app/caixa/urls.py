from django.urls import path
from . import views

urlpatterns = [
    path('', views.FechamentoCaixaView.as_view(), name='f_caixa'),
    path('gf_caixa', views.GetFechamentoCaixa.as_view(), name='gf_caixa'),
    path('sf_caixa', views.SetFechamentoCaixa.as_view(), name='sf_caixa'),
    path('g_depositos', views.GetDepositos.as_view(), name='g_depositos'),
    path('g_clientes', views.GetClientes.as_view(), name='g_clientes'),
    # reposição de caixa
    path('repo_caixa', views.ReposicaoCaixaView.as_view(), name='repo_caixa'),
]
