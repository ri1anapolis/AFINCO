from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('jsi18n', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('pages.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('depositos/', include('depositos.urls')),
    path('caixa/', include('caixa.urls')),
    path('clientes/', include('clientes.urls')),
    path('despesas/', include('despesas.urls')),
    path('cartoes/', include('api_cartoes.urls')),
]
