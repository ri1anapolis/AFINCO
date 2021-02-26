from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q, ProtectedError
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.template.defaultfilters import pluralize

from . import models, filters, forms

from rolepermissions.mixins import HasRoleMixin
from django_filters.views import FilterView
from sentry_sdk import capture_exception
from dal import autocomplete


class CategoriaDespesaAutocomplete(
    LoginRequiredMixin, HasRoleMixin, autocomplete.Select2QuerySetView
):
    allowed_roles = ["oficial", "contador"]

    def get_queryset(self):
        qs = models.CategoriaDespesa.objects.all()

        if self.q:
            qs = qs.filter(
                Q(ativo=True) & Q(identificacao__icontains=self.q)
                | Q(conta_credito__istartswith=self.q)
                | Q(conta_debito__istartswith=self.q)
                | Q(codigo_rf__istartswith=self.q)
            )

        return qs


class HistoricoDespesasAutocomplete(
    LoginRequiredMixin, HasRoleMixin, autocomplete.Select2QuerySetView
):
    allowed_roles = ["oficial", "contador"]

    def get_queryset(self):
        qs = models.HistoricosDespesas.objects.all()

        if self.q:
            qs = qs.filter(identificacao__icontains=self.q)

        return qs


#
### CATEGORIAS DE DESPESAS


class CategoriaDespesaListView(LoginRequiredMixin, HasRoleMixin, FilterView):
    allowed_roles = ["oficial", "contador"]
    model = models.CategoriaDespesa
    template_name = "categoria_despesa_list.html"
    filterset_class = filters.CategoriaDespesaFilter
    login_url = "login"
    paginate_by = 25


class CategoriaDespesaDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    allowed_roles = ["oficial", "contador"]
    model = models.CategoriaDespesa
    template_name = "categoria_despesa_detail.html"
    login_url = "login"


class CategoriaDespesaCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    allowed_roles = ["oficial", "contador"]
    model = models.CategoriaDespesa
    template_name = "categoria_despesa_new.html"
    form_class = forms.CategoriaDespesaForm
    login_url = "login"
    success_message = "A categoria de despesa foi criada com sucesso."

    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse("categoria_despesa_new")
        # else return the default `success_url`
        return super().get_success_url()


class CategoriaDespesaUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    allowed_roles = ["oficial", "contador"]
    model = models.CategoriaDespesa
    form_class = forms.CategoriaDespesaForm
    template_name = "categoria_despesa_edit.html"
    login_url = "login"
    success_message = "A categoria de despesa foi alterada com sucesso."


class CategoriaDespesaDeleteView(LoginRequiredMixin, HasRoleMixin, DeleteView):
    allowed_roles = ["oficial", "contador"]
    model = models.CategoriaDespesa
    template_name = "categoria_despesa_delete.html"
    login_url = "login"
    success_url = reverse_lazy("categoria_despesa_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            self.delete(request, *args, **kwargs)

        except ProtectedError as e:
            categoria_link = '<a href="' + reverse(
                "categoria_despesa_detail", args=[str(self.object.id)]
            )
            categoria_link += f'" target="_blank" rel="noopener">{self.object}</a>'

            _despesas_links = []
            _outros_objs = []

            for obj in e.protected_objects:

                if isinstance(e.protected_objects[0], models.Despesa):
                    _despesas_links.append(
                        '<a href="#'  # reverse('despesa_detail', args=[str(obj.id)])
                        + f'" target="_blank" rel="noopener">{obj}</a>'
                    )

                else:
                    _outros_objs.append(f"{obj}")

            _msg = f'Não foi possível remover a categoria de despesa "{categoria_link}" pois está relacionada '

            if _despesas_links:
                _links = ", ".join(_despesas_links)
                _msg += f"ao{pluralize(len(_despesas_links))} "
                _msg += f"servico{pluralize(len(_despesas_links))} {_links}"

            if _outros_objs:
                _o_objs = ", ".join(_outros_objs)
                if _despesas_links:
                    _msg += " e "
                _msg += f"ao{pluralize(len(_outros_objs))} "
                _msg += f"objeto{pluralize(len(_outros_objs))} {_o_objs}"

            messages.error(request, _msg)

            return redirect(self.object)

        else:
            messages.success(
                request,
                f'A categoria de despesa "{self.object}" foi removida com sucesso!',
            )
            return redirect(reverse("categoria_despesa_list"))


###
### DESPESAS


class DespesaListView(LoginRequiredMixin, HasRoleMixin, FilterView):
    allowed_roles = ["oficial", "contador"]
    model = models.Despesa
    template_name = "despesa_list.html"
    filterset_class = filters.DespesaFilter
    login_url = "login"
    paginate_by = 25


class DespesaDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    allowed_roles = ["oficial", "contador"]
    model = models.Despesa
    template_name = "despesa_detail.html"
    login_url = "login"


class DespesaCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    allowed_roles = ["oficial", "contador"]
    model = models.Despesa
    template_name = "despesa_new.html"
    form_class = forms.DespesaForm
    login_url = "login"
    success_message = "A categoria de despesa foi criada com sucesso."

    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse("despesa_new")
        # else return the default `success_url`
        return super().get_success_url()


class DespesaUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    allowed_roles = ["oficial", "contador"]
    model = models.Despesa
    form_class = forms.DespesaForm
    template_name = "despesa_edit.html"
    login_url = "login"
    success_message = "A categoria de despesa foi alterada com sucesso."


class DespesaDeleteView(LoginRequiredMixin, HasRoleMixin, DeleteView):
    allowed_roles = ["oficial", "contador"]
    model = models.Despesa
    template_name = "despesa_delete.html"
    login_url = "login"
    success_url = reverse_lazy("despesa_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            self.delete(request, *args, **kwargs)

        except Exception as e:
            messages.error(
                request,
                f'Não foi possível remover a despesa "{self.object}"! Erro: "{e}"',
            )

            return redirect(self.object)

        else:
            messages.success(
                request,
                f'A categoria de despesa "{self.object}" foi removida com sucesso!',
            )
            return redirect(reverse("despesa_list"))
