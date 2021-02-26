# pylint: disable=missing-module-docstring,broad-except
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.messages.views import SuccessMessageMixin
from django_filters.views import FilterView

from rolepermissions.mixins import HasRoleMixin

from . import models, forms, filters

User = get_user_model()
"""Variável para ser usada com o método form_valid.
Necessário pois o django vai buscar o usuário em django.contrib.auth.models.User,
e dessa forma sobrescrevemos o model user com o model customizado de contas."""


class DepositoListView(LoginRequiredMixin, FilterView):
    """Apresentação dos depósitos"""

    model = models.Depositos
    template_name = "deposito_list.html"
    login_url = "login"
    filterset_class = filters.DepositosFilter
    paginate_by = 25


class DepositoDetailView(LoginRequiredMixin, DetailView):
    """Visualiza detalhes do registro de depósito."""

    model = models.Depositos
    template_name = "deposito_detail.html"
    login_url = "login"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )  # Call the base implementation first to get a context

        context["fcaixa_list"] = self.model.objects.get(
            id=self.object.pk
        ).lancamentodeposito_set.select_related()

        context["clientes_pagamentos_list"] = self.model.objects.get(
            id=self.object.pk
        ).clientepagamentos_set.select_related()

        return context


class DepositoCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    """Cria novos registros."""

    allowed_roles = ["oficial", "contador"]
    model = models.Depositos
    template_name = "deposito_new.html"
    form_class = forms.DepositoCreateForm
    login_url = "login"
    success_message = 'O deposito "%(identificacao)s" foi criado com sucesso.'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse("deposito_new")

        return super().get_success_url()  # else return the default `success_url`


class DepositoUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    """Altera um registro de depósito bancário do banco de dados"""

    allowed_roles = ["oficial", "contador"]
    model = models.Depositos
    template_name = "deposito_edit.html"
    form_class = forms.DepositoCreateForm
    login_url = "login"
    success_message = 'O deposito "%(identificacao)s" foi alterado com sucesso.'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )  # Call the base implementation first to get a context
        context["fcaixa_list"] = self.model.objects.get(
            id=self.object.pk
        ).lancamentodeposito_set.select_related()

        context["clientes_pagamentos_list"] = self.model.objects.get(
            id=self.object.pk
        ).clientepagamentos_set.select_related()

        return context


class DepositoDeleteView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, DeleteView
):
    """Remove um registro de depósito do banco de dados"""

    allowed_roles = "oficial"
    model = models.Depositos
    template_name = "deposito_delete.html"
    login_url = "login"
    success_url = reverse_lazy("deposito_list")
    success_message = 'O deposito "%(identificacao)s" foi removido com sucesso.'

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError as error:
            # pylint: disable=attribute-defined-outside-init
            self.object = self.get_object()

            deposito_link = '<a href="' + reverse(
                "deposito_detail", args=[str(self.object.id)]
            )
            deposito_link += f'">{self.object.identificacao}</a>'

            f_caixa_links = ""
            for lancamento in error.args[1]:
                if len(f_caixa_links) > 0:
                    f_caixa_links += ", "
                f_caixa_links += (
                    '<a href="'
                    + reverse("f_caixa")
                    + f'?fcaixa_id={lancamento.fechamento_caixa.id}"'
                )
                f_caixa_links += f' target="_blank">{lancamento.fechamento_caixa}</a>'

            # passing the object is a shortcut to get_absolute_url from model
            messages.error(
                request,
                f'Não foi possível remover o depósito "{deposito_link}" '
                f"pois está vinculado ao(s) fechamento(s) de caixa: {f_caixa_links}",
            )
            return redirect(self.object)
