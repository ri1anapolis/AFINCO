# pylint: disable=missing-module-docstring,disable=missing-class-docstring,broad-except,pointless-string-statement
import re
import functools
from datetime import date
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import intcomma

from depositos.helper_functions import valores, consolidar
from depositos.models import Depositos

from localflavor.br.forms import BRCPFField, BRCNPJField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from sentry_sdk import capture_exception


from . import models


class CustomDateInput(forms.widgets.TextInput):
    """Custom date widget"""

    input_type = "date"


###
### CLIENTES SERVIÇOS


class ClienteServicosForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=models.Cliente.objects.filter(
            Q(outorgante=None) & Q(ativo=True)
        ).exclude(Q(verifica_saldo=True) & Q(saldo__lt=5)),
    )

    class Meta:
        model = models.ClienteServicos
        fields = "__all__"
        widgets = {
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super(ClienteServicosForm, self).__init__(*args, **kwargs)

        if "instance" in kwargs and kwargs["instance"]:
            if kwargs["instance"].fatura:
                self.fields["liquidado"].disabled = True

            if kwargs["instance"].caixa or kwargs["instance"].fatura:
                self.fields["cliente"].disabled = True
                self.fields["data"].disabled = True
                self.fields["tipo_protocolo"].disabled = True
                self.fields["protocolo"].disabled = True
                self.fields["contabilizar"].disabled = True
                self.fields["valor"].disabled = True

            saldo = 1
            if kwargs["instance"].cliente.saldo > 0:
                saldo = kwargs["instance"].cliente.saldo

            cqs = models.Cliente.objects.filter(
                (Q(outorgante=None) & Q(ativo=True))
                | Q(id=kwargs["instance"].cliente.id)
            ).exclude(
                (Q(verifica_saldo=True) & Q(saldo__lt=saldo))
                & ~Q(id=kwargs["instance"].cliente.id)
            )

            self.fields["cliente"].initial = cqs
            self.fields["cliente"].queryset = cqs

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        valor = cleaned_data.get("valor", 0)
        valor_inicial = getattr(self.instance, "valor", 0)

        if valor_inicial is None:
            valor_inicial = 0

        if cliente.verifica_saldo and (
            (float(cliente.saldo) + valor_inicial - valor) <= -1
        ):
            self.add_error(
                "cliente",
                "O cliente não possui saldo suficiente para custear o serviço. "
                f"(Saldo: R$ {cliente.saldo:.2f})",
            )
            self.add_error(
                "valor",
                f"O valor é superior em R$ {abs(float(cliente.saldo) + valor_inicial - valor):.2f} "
                "ao saldo do cliente.",
            )


###
### CLIENTES


class ClienteForm(forms.ModelForm):
    cpf = BRCPFField(
        required=False,
        label="CPF",
        help_text="Número cadastro de pessoa física.",
    )
    cnpj = BRCNPJField(
        required=False,
        label="CNPJ",
        help_text="Número cadastro nacional de pessoa jurídica.",
    )

    def only_numeric(self, _string):
        """It takes a string and removes all non numeric characters"""
        if isinstance(_string, str):
            return re.sub("[^0-9]", "", _string)
        return None

    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get("tipo_documento")
        outorgante = cleaned_data.get("outorgante", None)
        cpf = cleaned_data["cpf"] = self.only_numeric(cleaned_data.get("cpf"))
        cnpj = cleaned_data["cnpj"] = self.only_numeric(cleaned_data.get("cnpj"))
        cleaned_data["telefone"] = self.only_numeric(cleaned_data.get("telefone"))
        estrangeiro = cleaned_data.get("estrangeiro")

        if outorgante:
            cleaned_data["verifica_saldo"] = False

        if not cpf:
            cleaned_data["cpf"] = None

            if tipo_documento == "PF":
                self.add_error("cpf", "É necessário informar o CPF.")

        if not cnpj:
            cleaned_data["cnpj"] = None

            if tipo_documento == "PJ":
                self.add_error("cnpj", "É necessário informar o CNPJ.")

        if not estrangeiro:
            cleaned_data["estrangeiro"] = None

            if tipo_documento == "EX":
                self.add_error("estrangeiro", "É necessário informar o CPF.")

    class Meta:
        model = models.Cliente
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.fields["saldo"].disabled = True
        self.fields["saldo_faturado"].disabled = True
        self.fields["saldo_faturado"].widget = forms.HiddenInput()

        oqs = models.Cliente.objects.filter(
            ativo=True,
        )

        #  testa se há instancia válida para confrontar os valores
        if "instance" in kwargs and kwargs["instance"]:
            #  se o objeto já for outorgante de outro objeto, impede de ser outorgado
            if (
                kwargs["instance"].cliente_set.select_related()
                or kwargs["instance"].clientefaturas_set.select_related()
                or kwargs["instance"].clienteservicos_set.select_related()
                or kwargs["instance"].clientepagamentos_set.select_related()
            ):
                self.fields["outorgante"].disabled = True
                self.fields["outorgante"].widget = forms.HiddenInput()

            oqs = oqs.exclude(
                Q(id=kwargs["instance"].id) | ~Q(outorgante=None),
            )

        else:
            oqs = oqs.exclude(
                ~Q(outorgante=None),
            )

        self.fields["outorgante"].initial = oqs
        self.fields["outorgante"].queryset = oqs


###
### CLIENTE FATURAS


class ClienteFaturasCreateForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=models.Cliente.objects.filter(ativo=True).exclude(
            ~Q(outorgante=None),
        )
    )

    class Meta:
        model = models.ClienteFaturas
        fields = "__all__"
        widgets = {
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            )
        }


class ClienteFaturasForm(ClienteFaturasCreateForm):
    cliente = forms.ModelChoiceField(
        queryset=models.Cliente.objects.all().exclude(
            ~Q(outorgante=None),
        )
    )
    servicos = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.ClienteServicos.objects.filter(
            liquidado=False,
            fatura=None,
        ),
        widget=FilteredSelectMultiple(
            "Serviços",
            False,
        ),
    )

    class Media:
        css = {"all": ["admin/css/widgets.css"]}
        js = ["jsi18n"]  # Adding this javascript is crucial

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(Div("servicos"))

        super(ClienteFaturasForm, self).__init__(*args, **kwargs)
        if self.instance:

            try:
                if self.instance.liquidado:
                    self.fields["servicos"].disabled = True
                    self.fields["valor_servicos"].disabled = True
                    self.fields["valor_descontos"].disabled = True
                    self.fields["valor_fatura"].disabled = True
            except Exception:
                pass

            try:
                if self.instance.cliente:
                    self.fields["cliente"].disabled = True
            except Exception:
                pass

            try:
                self.fields[
                    "servicos"
                ].initial = self.instance.clienteservicos_set.all()

                self.fields[
                    "servicos"
                ].queryset = models.ClienteServicos.objects.filter(
                    Q(cliente=self.instance.cliente)
                    & (
                        Q(liquidado=False)
                        | (Q(liquidado=True) & Q(fatura=self.instance))
                    )
                    & (Q(fatura=None) | Q(fatura=self.instance))
                    & Q(contabilizar=True)
                )
            except Exception:
                pass

    def save(
        self, *args, **kwargs
    ):  # pylint: disable=unused-argument,signature-differs
        instance = super(ClienteFaturasForm, self).save(commit=False)

        try:
            self.fields["servicos"].initial.update(
                fatura=None,
                liquidado=False,
            )
            self.cleaned_data["servicos"].update(
                fatura=instance,
                liquidado=instance.liquidado,
            )
        except Exception:
            pass
        else:
            instance.save()

        return instance


###
### CLIENTE PAGAMENTOS


class ClientePagamentosForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=models.Cliente.objects.filter(ativo=True).exclude(
            ~Q(outorgante=None),
        )
    )
    deposito = forms.ModelChoiceField(
        queryset=Depositos.objects.filter(
            consolidado=False,
        ),
        required=False,
    )
    liquidar_faturas = forms.MultipleChoiceField(
        required=False,
        label="Liquidar Faturas",
        choices=[],
    )

    class Media:
        js = ("js/cliente_pagamentos_new.js",)

    class Meta:
        model = models.ClientePagamentos
        fields = "__all__"
        widgets = {
            "notas_adicionais": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            )
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.liquidar_faturas = []

        super(ClientePagamentosForm, self).__init__(*args, **kwargs)

        self.fields["usuario"].disabled = True
        self.fields["usuario"].widget = forms.HiddenInput()

        #  testa se há instancia válida para confrontar os valores
        if "instance" in kwargs and kwargs["instance"]:

            self.fields["deposito"].initial = self.instance.deposito
            if self.instance.deposito:
                self.fields["deposito"].queryset = Depositos.objects.filter(
                    valor__gte=self.instance.valor
                ).exclude(~Q(id=self.instance.deposito.id) & Q(consolidado=True))
            else:
                self.fields["deposito"].queryset = Depositos.objects.filter(
                    valor__gte=self.instance.valor,
                    consolidado=False,
                )

            """Uma vez que tenha sido criado, o formulário não permitirá
                alterar o cliente.
                Dentre outras coisas isso visa impedir complicações nas
                atualizações dos saldos dos clientes!
            """
            if self.instance.cliente:
                self.fields["cliente"].disabled = True
                self.fields["liquidar_faturas"].disabled = True
                self.fields["liquidar_faturas"].widget = forms.HiddenInput()

            if getattr(self.instance.deposito, "consolidado", False):
                self.fields["data_pagamento"].disabled = True
                self.fields["forma_pagamento"].disabled = True
                self.fields["valor"].disabled = True
                self.fields["deposito"].disabled = True

        if (kwargs.get("data") and kwargs["data"].get("cliente")) or (
            args and args[0].get("cliente")
        ):
            _cliente = (
                kwargs["data"]["cliente"]
                if kwargs.get("data") and kwargs["data"].get("cliente")
                else args[0].get("cliente")
            )
            _valor_fatura = (
                kwargs["data"]["valor"]
                if kwargs.get("data") and kwargs["data"].get("valor")
                else args[0].get("valor")
            )

            self.fields["liquidar_faturas"].choices = [
                (
                    fatura.pk,
                    f"{fatura.pk} - "
                    f"{date.strftime(fatura.data_fatura, '%d/%m/%Y')} - "
                    f"R$ {intcomma(fatura.valor_fatura)}",
                )
                for fatura in models.ClienteFaturas.objects.filter(
                    cliente=_cliente,
                    valor_fatura__lte=_valor_fatura,
                    liquidado=False,
                ).order_by(
                    "-data_fatura",
                    "-id",
                    "-valor_fatura",
                )
            ]

    def clean(self):
        cleaned_data = super().clean()
        data_pagamento = cleaned_data.get("data_pagamento")
        forma_pagamento = cleaned_data.get("forma_pagamento")
        deposito = cleaned_data.get("deposito")
        valor = cleaned_data.get("valor", 0) or 0
        cleaned_data["usuario"] = self.request.user
        liquidar_faturas = self.liquidar_faturas = self.data.getlist(
            "liquidar_faturas", []
        )
        cliente = cleaned_data.get("cliente", None)

        if deposito:
            valor_disponivel_deposito = valores(deposito)["valor_disponivel"]

        if forma_pagamento == "DP" and not deposito:
            self.add_error(
                "deposito",
                'Ao indicar "depósito" como forma de pagamento, '
                "deve-se relacionar um depósito ao pagamento!",
            )

        if deposito and forma_pagamento != "DP":
            self.add_error(
                "forma_pagamento",
                "Ao relacionar um depósito ao pagamento é necessário "
                "que a a forma de pagamento corresponda!",
            )

        if not data_pagamento:
            self.add_error(
                "data_pagamento", "É necessário informar a data do pagamento!"
            )

        if valor <= 10:
            self.add_error("valor", "O pagamento deve possuir um valor válido!")

        if "deposito" in self.changed_data and deposito:
            if deposito.consolidado:
                self.add_error(
                    "deposito",
                    "O depósito relacionado já está consolidado, "
                    "logo não é possível relacioná-lo ao pagamento!",
                )

            if valor_disponivel_deposito < valor:
                self.add_error(
                    "deposito",
                    "O depósito relacionado não possui saldo suficiente para "
                    "realizar o pagamento.",
                )

        if ("valor" in self.changed_data and deposito) and (
            "deposito" not in self.changed_data
        ):
            """se o valor mudar e o depósito continuar sendo o mesmo pode haver algum problema
            com a validação do valor disponível, pois o valor disponível informado no registro
            de depósito já está contando com o valor deste registro de pagamento, e ao alterar
            o valor do pagamento para um valor maior a validação vai falhar.
            Ex.: o depósito é de 800 e já tem 500 utilizado deste pagamento, caso se altere o
            valor destes pagamento para 501 a validação vai acusar não ter saldo suficiente, pois
            ele já estárá considerando os 500 como valor utilizado e vai tentar validar a utilização
            de mais 501!
            Pare resolver esse problema subtrairemos o valor atual do pagamento pelo seu valor
            inicial, assim, nesse tipo de caso em específico, a validação de disponibilidade de
            valor validará apenas a diferença (o valor a mais) que esteja sendo desejado!
            """
            if (
                valor_disponivel_deposito
                and valor_disponivel_deposito < valor - self.instance.valor
            ):
                self.add_error(
                    "valor",
                    "O valor desejado é superior ao valor disponível no depósito!",
                )
            if not valor_disponivel_deposito:
                self.add_error(
                    "deposito",
                    "O depósito não possui valores saldo disponível para uso!",
                )

        if len(liquidar_faturas) > 0:
            faturas = list(
                models.ClienteFaturas.objects.filter(id__in=(liquidar_faturas))
            )

            def reducer(total, fatura):
                if fatura.liquidado:
                    self.add_error(
                        "liquidar_faturas",
                        f"A fatura de ID {fatura.id} já foi liquidada!",
                    )
                if fatura.cliente != cliente:
                    self.add_error(
                        "liquidar_faturas",
                        f'A fatura de ID {fatura.id} não pertence ao cliente "{cliente}"!',
                    )
                return total + float(fatura.valor_fatura)

            valor_total_faturas = functools.reduce(reducer, faturas, 0)

            if valor_total_faturas > valor:
                self.add_error(
                    "liquidar_faturas",
                    "O valor total das faturas informadas "
                    f"(R$ {intcomma(round(valor_total_faturas, 2))})"
                    f" é superior ao valor do pagamento (R$ {intcomma(round(valor, 2))})!",
                )

    def save(
        self, *args, **kwargs
    ):  # pylint: disable=unused-argument,signature-differs
        instance = super(ClientePagamentosForm, self).save(commit=False)
        instance.save()

        if getattr(instance, "deposito", False):
            success, error = consolidar(  # pylint: disable=unused-variable
                instance.deposito,
                self.request.user,
            )

            if success:
                messages.info(
                    self.request,
                    f'O depósito "{instance.deposito}" foi consolidado ao '
                    f'salvar o pagamento "{instance}" !',
                )

        if len(self.liquidar_faturas) > 0:
            faturas = models.ClienteFaturas.objects.filter(id__in=self.liquidar_faturas)

            @transaction.atomic
            def liquida_faturas(faturas):
                valor_total_faturas = 0
                for fatura in faturas:
                    try:
                        with transaction.atomic():
                            valor_total_faturas += float(fatura.valor_fatura)

                            if valor_total_faturas > float(instance.valor):
                                raise Exception(
                                    "A soma dos valores das faturas é superior ao "
                                    "valor do pagamento"
                                )

                            if fatura.cliente != instance.cliente:
                                raise Exception(
                                    f'A fatura não pertence ao cliente "{instance.cliente}".'
                                )

                            fatura.liquidado = True
                            fatura.data_pagamento = timezone.now()
                            fatura.save()

                    except Exception as error:
                        capture_exception(error)
                        messages.warning(
                            self.request,
                            f'Ao tentar liquidar a fatura "{fatura}" ocorreu o erro: "{error}"',
                        )

            liquida_faturas(faturas)

        return instance
