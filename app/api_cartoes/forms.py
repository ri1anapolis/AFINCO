from django import forms
from django.utils import timezone
from decimal import Decimal

from . import models

from caixa.get_fcaixa import get_fcaixa_status


def falsey_but_not_none(valor):
    if valor is not None and (not valor or 
        (isinstance(valor, (int, float, Decimal)) and valor < 0)):
        return True
    else:
        return False


class ConfiguracoesForm(forms.ModelForm):
    class Meta:
        model = models.Configuracoes
        fields= '__all__'

    def clean(self):
        cleaned_data = super().clean()
        valor_custa_register = cleaned_data.get('valor_custa_register', 0)
        taxa_credito = cleaned_data.get('taxa_credito', 0)
        taxa_debito = cleaned_data.get('taxa_debito', 0)

        if falsey_but_not_none(valor_custa_register):
            self.add_error(
                'valor_custa_register',
                f'O valor da custa deve ser superior a 0.'
            )

        if falsey_but_not_none(taxa_credito):
            self.add_error(
                'taxa_credito',
                f'O valor da taxa deve ser superior a 0.'
            )
        
        if falsey_but_not_none(taxa_debito):
            self.add_error(
                'taxa_debito',
                f'O valor da taxa deve ser superior a 0.'
            )


class BandeirasForm(forms.ModelForm):
    class Meta:
        model = models.Bandeiras
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        usar_debito = cleaned_data.get('usar_debito', False)
        usar_credito = cleaned_data.get('usar_credito', False)
        taxa_debito = cleaned_data.get('taxa_debito', None)
        taxa_credito_avista = cleaned_data.get('taxa_credito_avista', None)
        parcelar = cleaned_data.get('parcelar', False)
        taxa_6meses = cleaned_data.get('taxa_6meses', False)
        parcelamento = cleaned_data.get('parcelamento', None)
        taxa_credito_parcelado = cleaned_data.get('taxa_credito_parcelado', None)
        taxa_credito_parcelado_porparcela = cleaned_data.get('taxa_credito_parcelado_porparcela', None)

        if not usar_debito and not usar_credito:
            cleaned_data['ativo'] = False

        if falsey_but_not_none(taxa_credito_avista):
            self.add_error(
                'taxa_credito_avista',
                f'O valor da taxa deve ser vazio ou superior a 0.'
            )

        if falsey_but_not_none(taxa_debito):
            self.add_error(
                'taxa_debito',
                f'O valor da taxa deve ser vazio ou superior a 0.'
            )
        
        if not parcelar and taxa_6meses:
            self.add_error(
                'taxa_6meses',
                'Para utilizar o "modo 6/6" é necessário habilitar o parcelamento.'
            )
        
        if not parcelamento and parcelar:
            self.add_error(
                'parcelamento',
                'Ao habilitar o parcelamento deve-se informar o número de parcelas permitidas.'
            )
        if falsey_but_not_none(parcelamento):
            self.add_error(
                'parcelamento',
                f'A quantidade de parcelas deve ser {"" if parcelar else "vazio ou "}superior a 1.'
            )

        if not taxa_credito_parcelado and parcelar:
            self.add_error(
                'taxa_credito_parcelado',
                'Ao habilitar o parcelamento deve-se informar a taxa.'
            )
        if falsey_but_not_none(taxa_credito_parcelado):
            self.add_error(
                'taxa_credito_parcelado',
                f'O valor da taxa deve ser  {"" if parcelar else "vazio ou "}superior a 0.'
            )

        if falsey_but_not_none(taxa_credito_parcelado_porparcela) and taxa_credito_parcelado_porparcela < 0:
            self.add_error(
                'taxa_credito_parcelado_porparcela',
                f'O valor da taxa deve ser vazio, 0 ou número positivo.'
            )


class RegistrosCartoesForm(forms.ModelForm):
    class Meta:
        model = models.RegistrosCartoes
        fields= '__all__'
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.from_my_view = kwargs.pop('from_my_view', False)

        super(RegistrosCartoesForm, self).__init__(*args, **kwargs)

        if self.from_my_view and self.request.user:
            self.fields['usuario'].required = False

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        data_registros = cleaned_data.get('data_registros')
        operacao = cleaned_data.get('operacao')
        valor_servico = float(cleaned_data.get('valor_servico', 0))
        valor_cobrado = float(cleaned_data.get('valor_cobrado', 0))
        taxa_juros = float(cleaned_data.get('taxa_juros', 0))

        if not usuario:
            usuario = cleaned_data['usuario'] = self.request.user
        
        if not data_registros:
            data_registros = cleaned_data['data_registros'] = timezone.now()

        fcaixa_status = get_fcaixa_status(usuario.id, data_registros)
        if fcaixa_status == 'consolidado':
            self.add_error(
                'data_registro',
                'O registro não pode ser salvo pois o fechamento de caixa está consolidado.'
            )

        if operacao != models.RegistrosCartoes.CREDITO:
            cleaned_data['parcelas'] = None
        
        if valor_servico <= 0 :
            self.add_error(
                'valor_servico',
                'O valor do serviço deve ser maior que zero.'
            )
        if valor_cobrado <= 0 :
            self.add_error(
                'valor_cobrado',
                'O valor cobrado deve ser maior que zero.'
            )
        if taxa_juros <= 0 :
            self.add_error(
                'taxa_juros',
                'A taxa de juros deve ser maior que zero.'
            )

        if all([valor_servico, valor_cobrado, taxa_juros]):
            prova_valor_cobrado = valor_servico / (1 - (taxa_juros / 100))

            if abs(valor_cobrado - prova_valor_cobrado) > 0.07:
                self.add_error(
                    'valor_cobrado',
                    'O cálculo sobre a taxa e valor do serviço indicados deveria '
                    f'ter por resultado R${prova_valor_cobrado:.2f}.'
                )

        return cleaned_data
