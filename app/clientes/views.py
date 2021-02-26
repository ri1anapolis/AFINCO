# pylint: disable=missing-module-docstring,missing-class-docstring,broad-except,attribute-defined-outside-init
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import ProtectedError, Q, Sum
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.template.defaultfilters import pluralize
from django.utils import timezone
from django.core.exceptions import ValidationError
from rolepermissions.mixins import HasRoleMixin
from django_filters.views import FilterView

from .helper_functions import get_cliente_faturas
from . import models, forms, filters


# CADASTROS DE CLIENTES


class GetClienteFaturas(View):
    """Retorna as faturas do cliente"""

    # allowed_roles = ["oficial", "contador", "supervisor_atendimento"]

    def get(self, request):
        """Responde chamadas GET com lista de faturas do cliente indicado"""
        cliente_id = self.request.GET.get("cliente_id")
        valor_fatura = self.request.GET.get("valor_fatura")

        return JsonResponse(
            get_cliente_faturas(
                cliente=cliente_id,
                valor_fatura=valor_fatura,
                liquidadas=False,
            ),
            safe=False,
        )


class ClienteConta:
    def _get_cliente_obj(self, cliente):
        """Retorna o objeto do cliente"""

        if isinstance(cliente, models.Cliente):
            return cliente

        try:
            return models.Cliente.objects.get(id=cliente)
        except Exception:
            pass

        return None

    def valor_receitas(self, cliente):
        """Todas as receitas (valores que incrementam a conta) do cliente"""

        cliente = self._get_cliente_obj(cliente)

        if cliente:
            valor = cliente.clientepagamentos_set.select_related().aggregate(
                Sum("valor")
            )["valor__sum"]

            return float(valor) if valor else 0

        return None

    def valor_despesas_faturadas(self, cliente):
        """Todos as despesas faturadas (valor total de todas as faturas) do cliente"""
        cliente = self._get_cliente_obj(cliente)

        if cliente:
            valor = cliente.clientefaturas_set.select_related().aggregate(
                Sum("valor_fatura")
            )["valor_fatura__sum"]
            return float(valor) if valor else 0

        return None

    def valor_despesas_compromissadas(self, cliente):
        """Todas as despesas compromissadas (serviços contabilizáveis não faturados)
        do cliente."""
        cliente = self._get_cliente_obj(cliente)

        if cliente:
            valor = (
                cliente.clienteservicos_set.select_related()
                .exclude(Q(contabilizar=False) | Q(liquidado=True) | ~Q(fatura=None))
                .aggregate(Sum("valor"))["valor__sum"]
            )
            return float(valor) if valor else 0

        return None

    def saldo_faturado(self, cliente):
        """Saldo resultante da subtração entre as despesas faturadas e as receitas.
        Seu principal uso é prover um saldo de menor atualização e, portanto,
        impacto no sistema, para ser usado na composição do saldo líquido,
        que será atualizado nas operações com serviços, ou seja, mais frequente-
        mente. Esse modelo visa mitigar possíveis problemas com desempenho a
        longo prazo visto que a composição dos saldos depende do recalculo de
        todos os itens relacionados (pagamentos, faturas, serviços).
        """
        valor_receitas = self.valor_receitas(cliente)
        valor_faturadas = self.valor_despesas_faturadas(cliente)

        if valor_receitas is not None and valor_faturadas is not None:
            return valor_receitas - valor_faturadas

        return None

    def saldo_liquido(self, cliente, saldo_faturado=False):
        """Saldo resultante da subtração entre as despesas compromissadas e o saldo
        faturado.
        Seu principal uso é prover um saldo para uso geral, principalmente para
        verificação da disponibilidade de recursos do cliente para o lançamento
        de mais serviços.
        Esse modelo visa mitigar possíveis problemas com desempenho a
        longo prazo visto que a composição dos saldos depende do recalculo de
        todos os itens relacionados (pagamentos, faturas, serviços).
        Se fornecido o valor 'True' para o atributo 'saldo_faturado', serão
        retornados tando o saldo líquido quando o saldo faturado, em um tupla!
        (saldo_liquido, saldo_faturado)
        """
        cliente = self._get_cliente_obj(cliente)

        if cliente:
            saldo_liquido = float(
                cliente.saldo_faturado
            ) - self.valor_despesas_compromissadas(cliente)

            if saldo_faturado is True:
                return saldo_liquido, saldo_faturado

            return saldo_liquido

        return None

    def test_valor(self, cliente, valor):
        """Verifica se o valor indicado pode ser utilizado para adicionar novo
        serviço ao cliente.
        """

        cliente = self._get_cliente_obj(cliente)

        if cliente:
            if cliente.verifica_saldo:
                saldo_liquido = self.saldo_liquido(cliente)
                if (saldo_liquido - float(valor)) <= -1:
                    return False

            return True

        return None


class ClienteListView(LoginRequiredMixin, HasRoleMixin, ListView):
    """Apresentação dos clientes"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.Cliente
    template_name = "cliente_list.html"
    login_url = "login"
    queryset = model.objects.all().exclude(~Q(outorgante=None))


class ClienteDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    """Visualiza detalhes do registro de cliente."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.Cliente
    template_name = "cliente_detail.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["outorgados_list"] = self.model.objects.get(
            id=self.object.id
        ).cliente_set.select_related()

        if "print" in self.request.GET and not self.object.outorgante:
            context["print"] = True

            faturas = self.model.objects.get(
                id=self.object.id
            ).clientefaturas_set.select_related()

            pagamentos = self.model.objects.get(
                id=self.object.id
            ).clientepagamentos_set.select_related()

            conta = []
            for _fatura in faturas:
                conta.append({"data": _fatura.data_fatura, "fatura": _fatura})
            for pagamento in pagamentos:
                conta.append({"data": pagamento.data_pagamento, "pagamento": pagamento})

            context["extrato_conta"] = sorted(conta, key=lambda conta: conta["data"])
            context["vlr_desp_compr"] = self.object.saldo_faturado - self.object.saldo

        return context


class ClienteCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    """Cria novo cliente."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.Cliente
    form_class = forms.ClienteForm
    template_name = "cliente_new.html"
    login_url = "login"
    success_message = 'O cliente "%(nome)s" foi criado com sucesso.'


class ClienteUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    """Altera um cliente"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.Cliente
    form_class = forms.ClienteForm
    template_name = "cliente_edit.html"
    login_url = "login"
    success_message = 'O cliente "%(nome)s" foi alterado com sucesso.'


class ClienteDeleteView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, DeleteView
):
    """Remove cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.Cliente
    template_name = "cliente_delete.html"
    login_url = "login"
    success_url = reverse_lazy("cliente_list")
    success_message = 'O cliente "%(nome)s" foi removido com sucesso.'

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError as error:
            self.object = self.get_object()

            servicos = ""
            for servico in error.args[1]:
                if servicos != "":
                    servicos += ", "
                servicos += '<a href="' + reverse(
                    "cliente_servicos_detail", args=[str(servico.id)]
                )
                servicos += f'" target="_blank" rel="noopener">{servico.tipo_protocolo}.{servico.protocolo}</a>'

            # passing the object is a shortcut to get_absolute_url from model
            messages.error(
                request,
                f'Não foi possível remover o cliente "{self.object}"'
                f" pois está sendo utilizado pelos seguintes serviços:\n{servicos}",
            )
            return redirect(self.object)


# PERFIS DE CLIENTES


class PerfilClienteListView(LoginRequiredMixin, HasRoleMixin, ListView):
    """Apresentação dos perfis clientes"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.PerfilCliente
    template_name = "perfil_cliente_list.html"
    login_url = "login"


class PerfilClienteDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    """Visualiza detalhes dos  perfís de clientes."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.PerfilCliente
    template_name = "perfil_cliente_detail.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["clientes_list"] = self.model.objects.get(
            id=self.object.pk
        ).cliente_set.select_related()

        return context


class PerfilClienteCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    """Cria novo perfil de cliente."""

    allowed_roles = ["oficial", "contador"]
    model = models.PerfilCliente
    fields = ["nome", "descricao", "periodo_pag", "ativo"]
    template_name = "perfil_cliente_new.html"
    login_url = "login"
    success_message = 'O perfil de cliente "%(nome)s" foi criado com sucesso.'


class PerfilClienteUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    """Altera um perfil cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.PerfilCliente
    fields = ["nome", "descricao", "periodo_pag", "ativo"]
    template_name = "perfil_cliente_edit.html"
    login_url = "login"
    success_message = 'O perfil de cliente "%(nome)s" foi alterado com sucesso.'


class PerfilClienteDeleteView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, DeleteView
):
    """Remove perfil de cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.PerfilCliente
    template_name = "perfil_cliente_delete.html"
    login_url = "login"
    success_url = reverse_lazy("perfil_cliente_list")
    success_message = 'O perfil de cliente "%(nome)s" foi removido com sucesso.'


# SERVIÇOS AOS CLIENTES


class ClienteServicosListView(LoginRequiredMixin, HasRoleMixin, FilterView):
    """Apresentação dos serviços aos clientes"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClienteServicos
    template_name = "cliente_servicos_list.html"
    filterset_class = filters.ClienteServicosFilter
    login_url = "login"
    paginate_by = 25


class ClienteServicosDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    """Visualiza detalhes dos serviços aos clientes."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClienteServicos
    template_name = "cliente_servicos_detail.html"
    login_url = "login"


class ClienteServicosCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    """Adicionar novo serviço ao cliente."""

    allowed_roles = ["oficial", "contador"]
    model = models.ClienteServicos
    form_class = forms.ClienteServicosForm
    template_name = "cliente_servicos_new.html"
    login_url = "login"
    success_message = "O serviço foi criado com sucesso."

    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse("cliente_servicos_new")
        # else return the default `success_url`
        return super().get_success_url()


class ClienteServicosUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    """Altera um serviço ao cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.ClienteServicos
    form_class = forms.ClienteServicosForm
    template_name = "cliente_servicos_edit.html"
    login_url = "login"
    success_message = "O serviço foi alterado com sucesso."


class ClienteServicosDeleteView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, DeleteView
):
    """Remove serviço ao cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.ClienteServicos
    template_name = "cliente_servicos_delete.html"
    login_url = "login"
    success_url = reverse_lazy("cliente_servicos_list")
    success_message = "O serviço foi removido com sucesso."

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError as error:
            self.object = self.get_object()

            servico_link = '<a href="' + reverse(
                "cliente_servicos_detail", args=[str(self.object.id)]
            )
            servico_link += f'" target="_blank" rel="noopener">ID{self.object.id}V{self.object.valor}</a>'

            if error.args[1].caixa:
                f_caixa_link = (
                    '<a href="'
                    + reverse("f_caixa")
                    + f"?fcaixa_id={error.args[1].caixa.id}"
                )
                f_caixa_link += (
                    f'" target="_blank" rel="noopener">{error.args[1].caixa}</a>'
                )

                # passing the object is a shortcut to get_absolute_url from model
                messages.error(
                    request,
                    f'Não foi possível remover o serviço "{servico_link}" '
                    f"pois está vinculado a um fechamento de caixa: {f_caixa_link}",
                )
            elif error.args[1].fatura:
                fatura_link = '<a href="' + reverse(
                    "cliente_faturas_detail", args=[str(error.args[1].fatura.id)]
                )
                fatura_link += (
                    f'" target="_blank" rel="noopener">{error.args[1].fatura}</a>'
                )

                messages.error(
                    request,
                    f'Não foi possível remover o serviço "{servico_link}" '
                    f"pois está vinculado à fatura: {fatura_link}",
                )

            return redirect(self.object)


# FATURAS DOS CLIENTES


class ClienteFaturasListView(LoginRequiredMixin, HasRoleMixin, FilterView):
    """Apresentação das faturas dos clientes"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClienteFaturas
    template_name = "cliente_faturas_list.html"
    filterset_class = filters.ClienteFaturasFilter
    login_url = "login"
    paginate_by = 25

    def get_success_url(self):  # pylint: disable=missing-function-docstring
        return reverse_lazy("cliente_faturas_detail", kwargs={"pk": self.object.pk})


class ClienteFaturasDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    """Visualizar detalhes das faturas dos clientes."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClienteFaturas
    template_name = "cliente_faturas_detail.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "servicos_relacionados"
        ] = self.get_object().clienteservicos_set.select_related()

        if "print" in self.request.GET:
            context["print"] = True

        return context


class ClienteFaturasCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    """Adicionar nova fatura ao cliente."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClienteFaturas
    form_class = forms.ClienteFaturasCreateForm
    template_name = "cliente_faturas_new.html"
    login_url = "login"
    success_message = "A fatura foi criada com sucesso."

    def get_success_url(self):
        return reverse_lazy("cliente_faturas_edit", kwargs={"pk": self.object.pk})


class ClienteFaturasUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    """Altera uma fatura do cliente"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClienteFaturas
    form_class = forms.ClienteFaturasForm
    template_name = "cliente_faturas_edit.html"
    login_url = "login"
    success_message = "A fatura foi alterada com sucesso."


class ClienteFaturasDeleteView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, DeleteView
):
    """Remove fatura do cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.ClienteFaturas
    template_name = "cliente_faturas_delete.html"
    login_url = "login"
    success_url = reverse_lazy("cliente_faturas_list")
    success_message = "A fatura foi removida com sucesso."

    def post(self, request, *args, **kwargs):
        try:
            return self.delete(request, *args, **kwargs)
        except ProtectedError as error:
            self.object = self.get_object()

            fatura_link = '<a href="' + reverse(
                "cliente_faturas_detail", args=[str(self.object.id)]
            )
            fatura_link += f'" target="_blank" rel="noopener">{self.object}</a>'

            _servicos_links = []
            _outros_objs = []

            for obj in error.protected_objects:

                if isinstance(error.protected_objects[0], models.ClienteServicos):
                    _servicos_links.append(
                        '<a href="'
                        + reverse("cliente_servicos_detail", args=[str(obj.id)])
                        + f'" target="_blank" rel="noopener">{obj}</a>'
                    )

                else:
                    _outros_objs.append(f"{obj}")

            _msg = f"Não foi possível remover a fatura {fatura_link} pois está relacionada "

            if _servicos_links:
                _links = ", ".join(_servicos_links)
                _msg += f"ao{pluralize(len(_servicos_links))} "
                _msg += f"servico{pluralize(len(_servicos_links))} {_links}"

            if _outros_objs:
                _o_objs = ", ".join(_outros_objs)
                if _servicos_links:
                    _msg += " e "
                _msg += f"ao{pluralize(len(_outros_objs))} "
                _msg += f"objeto{pluralize(len(_outros_objs))} {_o_objs}"

            messages.error(request, _msg)

            return redirect(self.object)

        else:
            messages.success(
                request, f"A fatura {self.object} foi removida com sucesso!"
            )


# PAGAMENTOS DOS CLIENTES


class ClientePagamentosListView(LoginRequiredMixin, HasRoleMixin, FilterView):
    """Apresentação dos pagamentos dos clientes"""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClientePagamentos
    template_name = "cliente_pagamentos_list.html"
    filterset_class = filters.ClientePagamentosFilter
    login_url = "login"
    paginate_by = 25


class ClientePagamentosDetailView(LoginRequiredMixin, HasRoleMixin, DetailView):
    """Visualizar detalhes dos pagamentos dos clientes."""

    allowed_roles = ["oficial", "contador", "supervisor_atendimento"]
    model = models.ClientePagamentos
    template_name = "cliente_pagamentos_detail.html"
    login_url = "login"


class ClientePagamentosCreateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, CreateView
):
    """Adicionar novo pagamento ao cliente."""

    allowed_roles = ["oficial", "contador"]
    model = models.ClientePagamentos
    form_class = forms.ClientePagamentosForm
    template_name = "cliente_pagamentos_new.html"
    login_url = "login"
    success_message = "O pagamento foi adicionado com sucesso."

    def get_success_url(self):
        if "another" in self.request.POST:
            return reverse("cliente_pagamentos_new")
        # else return the default `success_url`
        return super().get_success_url()

    def get_form_kwargs(self):
        kwargs = super(ClientePagamentosCreateView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


class ClientePagamentosUpdateView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, UpdateView
):
    """Altera uma fatura do cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.ClientePagamentos
    form_class = forms.ClientePagamentosForm
    template_name = "cliente_pagamentos_edit.html"
    login_url = "login"
    success_message = "O pagamento foi alterado com sucesso."

    def get_form_kwargs(self):
        kwargs = super(ClientePagamentosUpdateView, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs


class ClientePagamentosDeleteView(
    LoginRequiredMixin, HasRoleMixin, SuccessMessageMixin, DeleteView
):
    """Remove pagamento do cliente"""

    allowed_roles = ["oficial", "contador"]
    model = models.ClientePagamentos
    template_name = "cliente_pagamentos_delete.html"
    login_url = "login"
    success_url = reverse_lazy("cliente_pagamentos_list")
    success_message = "O pagamento foi removido com sucesso."

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            if abs(
                (self.object.data_add - timezone.now().date()).days
            ) > 30 and not getattr(request.user, "is_superuser", False):
                raise ValidationError(
                    "A remoção deste pagamento é permitida apenas aos administradores."
                )
            return self.delete(request, *args, **kwargs)

        except ValidationError as error:
            messages.error(
                request,
                f'Não foi possível remover o pagamento {self.object}: "{error}"',
            )

            return redirect(self.object)

        except ProtectedError as error:

            pagamento_link = '<a href="' + reverse(
                "cliente_pagamentos_detail", args=[str(self.object.id)]
            )
            pagamento_link += f'" target="_blank" rel="noopener">{self.object}</a>'

            if getattr(error.args[1], "deposito", False):
                deposito_link = '<a href="' + reverse(
                    "deposito_detail", args=[str(error.args[1].deposito.id)]
                )
                deposito_link += (
                    f'" target="_blank" rel="noopener">{error.args[1].deposito}</a>'
                )

                # passing the object is a shortcut to get_absolute_url from model
                messages.error(
                    request,
                    f'Não foi possível remover o pagamento "{pagamento_link}" '
                    f"pois está vinculado a um depósito: {deposito_link}",
                )

            else:
                _outros_objs = []

                for obj in error.protected_objects:
                    _outros_objs.append(f"{obj}")

                _msg = (
                    f"Não foi possível remover o pagamento {pagamento_link}"
                    "pois está relacionado "
                )

                if _outros_objs:
                    _o_objs = ", ".join(_outros_objs)
                    _msg += f"ao{pluralize(len(_outros_objs))} "
                    _msg += f"objeto{pluralize(len(_outros_objs))} {_o_objs}"

                messages.error(request, _msg)

            return redirect(self.object)

        else:
            messages.success(
                request, f"O pagamento {self.object} foi removido com sucesso!"
            )
