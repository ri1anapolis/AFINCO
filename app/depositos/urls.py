# pylint: disable=missing-module-docstring
from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.DepositoListView.as_view(),
        name="deposito_list",
    ),
    path(
        "new/",
        views.DepositoCreateView.as_view(),
        name="deposito_new",
    ),
    path(
        "<int:pk>/detail/",
        views.DepositoDetailView.as_view(),
        name="deposito_detail",
    ),
    path(
        "<int:pk>/edit/",
        views.DepositoUpdateView.as_view(),
        name="deposito_edit",
    ),
    path(
        "<int:pk>/delete/",
        views.DepositoDeleteView.as_view(),
        name="deposito_delete",
    ),
]
