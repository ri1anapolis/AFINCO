from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.ApiCartoes.as_view(), name='api_cartoes'),
    path('reg/api/', views.ApiRegistrosCartoes.as_view(), name='api_regcartoes'),
    path('', views.Cartoes.as_view(), name='cartoes'),
    path('reg/new', views.RegistrosCartoesCreate.as_view(), name='regcartoes_new'),
    path('reg/<int:pk>/recibo/', views.RegistrosCartoesRecibo.as_view(), name='regcartoes_recibo'),
    path('reg/<int:pk>/delete/', views.RegistrosCartoesDeleteView.as_view(), name='regcartoes_delete'),
]
