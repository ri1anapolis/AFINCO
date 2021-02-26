from django import forms
from django.forms import Textarea

from . import models


class CustomDateInput(forms.widgets.TextInput):
    """Custom date widget"""
    input_type = 'date'


class DepositoCreateForm(forms.ModelForm):
    class Meta:
        model = models.Depositos
        fields = (
            'data_deposito',
            'valor',
            'identificacao',
            'observacoes',
            'consolidado',
        )

    def __init__(self, *args, **kwargs):
        super(DepositoCreateForm, self).__init__(*args, **kwargs)
        self.fields['data_deposito'].widget = CustomDateInput()
        self.fields['observacoes'].widget = Textarea(
            attrs={'rows': 3, }
        )

        try:
            if (
                kwargs['instance'].lancamentodeposito_set.select_related() or
                kwargs['instance'].clientepagamentos_set.select_related()
            ):
                self.fields['data_deposito'].disabled = True
                self.fields['valor'].disabled = True
                self.fields['identificacao'].disabled = True
        except Exception:
            pass
