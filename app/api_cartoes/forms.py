from django import forms
from django.utils import timezone
from decimal import Decimal

from . import models

from caixa.get_fcaixa import get_fcaixa_status


class ConfiguracoesForm(forms.ModelForm):
    class Meta:
        model = models.Configuracoes
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["valor_custa_register"] = cleaned_data.get(
            "valor_custa_register", 0
        )
        cleaned_data["taxa_credito"] = cleaned_data.get("taxa_credito", 0)
        cleaned_data["taxa_debito"] = cleaned_data.get("taxa_debito", 0)


class BandeirasForm(forms.ModelForm):
    class Meta:
        model = models.Bandeiras
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        usar_debito = cleaned_data.get("usar_debito", False)
        usar_credito = cleaned_data.get("usar_credito", False)
        parcelar = cleaned_data.get("parcelar", False)
        taxa_6meses = cleaned_data.get("taxa_6meses", False)
        parcelamento = cleaned_data.get("parcelamento", None)
        taxa_credito_parcelado = cleaned_data.get("taxa_credito_parcelado", None)
        taxa_credito_parcelado_porparcela = cleaned_data.get(
            "taxa_credito_parcelado_porparcela", None
        )

        if not usar_debito and not usar_credito:
            cleaned_data["ativo"] = False

        if not parcelar and taxa_6meses:
            self.add_error(
                "taxa_6meses",
                'Para utilizar o "modo 6/6" é necessário habilitar o parcelamento.',
            )

        if not parcelamento and parcelar:
            self.add_error(
                "parcelamento",
                "Ao habilitar o parcelamento deve-se informar o número de parcelas permitidas.",
            )
        if parcelamento is not None and parcelamento < 2:
            self.add_error(
                "parcelamento",
                f'A quantidade de parcelas deve ser {"" if parcelar else "vazio ou "}superior a 1.',
            )

        if taxa_credito_parcelado is None and parcelar:
            self.add_error(
                "taxa_credito_parcelado",
                "Ao habilitar o parcelamento deve-se informar a taxa.",
            )

        if taxa_credito_parcelado is not None and taxa_credito_parcelado < 0:
            self.add_error(
                "taxa_credito_parcelado",
                f'O valor da taxa deve ser  {"" if parcelar else "vazio ou "}igual ou superior a 0.',
            )

        if (
            taxa_credito_parcelado_porparcela is not None
            and taxa_credito_parcelado_porparcela < 0
        ):
            self.add_error(
                "taxa_credito_parcelado_porparcela",
                f"O valor da taxa deve ser vazio, 0 ou número positivo.",
            )


class RegistrosCartoesForm(forms.ModelForm):
    class Meta:
        model = models.RegistrosCartoes
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.from_my_view = kwargs.pop("from_my_view", False)

        super(RegistrosCartoesForm, self).__init__(*args, **kwargs)

        if self.from_my_view and self.request.user:
            self.fields["usuario"].required = False

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get("usuario")
        data_registros = cleaned_data.get("data_registros")
        operacao = cleaned_data.get("operacao")
        valor_servico = float(cleaned_data.get("valor_servico", 0))
        valor_cobrado = float(cleaned_data.get("valor_cobrado", 0))
        taxa_juros = float(cleaned_data.get("taxa_juros", 0))

        if not usuario:
            usuario = cleaned_data["usuario"] = self.request.user

        if not data_registros:
            data_registros = cleaned_data["data_registros"] = timezone.now()

        fcaixa_status = get_fcaixa_status(usuario.id, data_registros)
        if fcaixa_status == "consolidado":
            self.add_error(
                "data_registro",
                "O registro não pode ser salvo pois o fechamento de caixa está consolidado.",
            )

        if operacao != models.RegistrosCartoes.CREDITO:
            cleaned_data["parcelas"] = None

        if valor_servico <= 0:
            self.add_error(
                "valor_servico", "O valor do serviço deve ser maior que zero."
            )
        if valor_cobrado <= 0:
            self.add_error("valor_cobrado", "O valor cobrado deve ser maior que zero.")

        if taxa_juros < 0:
            self.add_error(
                "taxa_juros", "A taxa de juros deve ser maior ou igual a zero."
            )

        if all([valor_servico, valor_cobrado, taxa_juros]):
            TROCO_IGNORAVEL = 0.05
            prova_valor_cobrado = valor_servico / (1 - (taxa_juros / 100))

            if abs(valor_cobrado - prova_valor_cobrado) > TROCO_IGNORAVEL:
                self.add_error(
                    "valor_cobrado",
                    "O cálculo sobre a taxa e valor do serviço indicados deveria "
                    f"ter por resultado R${prova_valor_cobrado:.2f}.",
                )

        return cleaned_data
