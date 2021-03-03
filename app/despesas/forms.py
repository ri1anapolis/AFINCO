# pylint: disable=missing-module-docstring,missing-class-docstring
from django import forms
from dal import autocomplete

from . import models


class CategoriaDespesaForm(forms.ModelForm):
    class Meta:
        model = models.CategoriaDespesa
        fields = "__all__"


class DespesaForm(forms.ModelForm):
    class Media:
        js = ["js/despesas.js"]

    class Meta:
        model = models.Despesa
        fields = "__all__"
        widgets = {
            "valor": forms.NumberInput(
                attrs={
                    "min": 0,
                }
            ),
            "identificacao": autocomplete.ModelSelect2(
                url="historico-autocomplete",
            ),
            "categoria_despesa": autocomplete.ModelSelect2(
                url="catdespesa-autocomplete",
            ),
            "observacoes": forms.Textarea(
                attrs={
                    "rows": 2,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        categoria_despesa = cleaned_data.get("categoria_despesa")
        busca_historico = cleaned_data.get("busca_historico", None)

        if busca_historico:
            cleaned_data["identificacao"] = busca_historico

        if (
            categoria_despesa
            and "categoria_despesa" in self.changed_data
            and not categoria_despesa.ativo
        ):
            self.add_error(
                "categoria_despesa",
                "A categoria selecionada não pode ser utilizada pois "
                "encontra-se desativada!",
            )
