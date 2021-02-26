# pylint: disable=missing-module-docstring
from django.urls import path
from . import views

urlpatterns = [
    ### categorias de despesas
    path(
        "catdespesa-autocomplete/",
        views.CategoriaDespesaAutocomplete.as_view(),
        name="catdespesa-autocomplete",
    ),
    path(
        "categorias/",
        views.CategoriaDespesaListView.as_view(),
        name="categoria_despesa_list",
    ),
    path(
        "categorias/new/",
        views.CategoriaDespesaCreateView.as_view(),
        name="categoria_despesa_new",
    ),
    path(
        "categorias/<int:pk>/detail/",
        views.CategoriaDespesaDetailView.as_view(),
        name="categoria_despesa_detail",
    ),
    path(
        "categorias/<int:pk>/edit/",
        views.CategoriaDespesaUpdateView.as_view(),
        name="categoria_despesa_edit",
    ),
    path(
        "categorias/<int:pk>/delete/",
        views.CategoriaDespesaDeleteView.as_view(),
        name="categoria_despesa_delete",
    ),
    ### despesas
    path(
        "historico-autocomplete/",
        views.HistoricoDespesasAutocomplete.as_view(
            create_field="identificacao",
        ),
        name="historico-autocomplete",
    ),
    path(
        "",
        views.DespesaListView.as_view(),
        name="despesa_list",
    ),
    path(
        "new/",
        views.DespesaCreateView.as_view(),
        name="despesa_new",
    ),
    path(
        "<int:pk>/detail/",
        views.DespesaDetailView.as_view(),
        name="despesa_detail",
    ),
    path(
        "<int:pk>/edit/",
        views.DespesaUpdateView.as_view(),
        name="despesa_edit",
    ),
    path(
        "<int:pk>/delete/",
        views.DespesaDeleteView.as_view(),
        name="despesa_delete",
    ),
]
