from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

import uuid
import random

def random_number():
    return random.randint(300, 1000)

def random_uuid_str():
    return str(uuid.uuid1())


class Configuracoes(models.Model):
    nome = models.CharField(
        max_length=50,
        unique=True,
        default=random_uuid_str,
        verbose_name='Nome',
        help_text='Nome dado à configuração.'
    )
    precedencia = models.PositiveIntegerField(
        unique=True,
        default=random_number,
        verbose_name='Precedência',
        help_text='Importância da configuração. Quanto maior o número, menor a precedência.'
    )
    valor_custa_register = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor da custa',
        help_text='Valor da custa utilizada no register.',
    )
    taxa_credito = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name='Taxa a crédito',
        help_text='Taxa padrão a crédito.',
    )
    taxa_debito = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        verbose_name='Taxa a débito',
        help_text='Taxa padrão a débito.',
    )

    def __str__(self):
        return f'{self.id}. {self.nome}'
    
    class Meta:
        verbose_name = 'Configuração'
        verbose_name_plural = 'Configurações'


class Bandeiras(models.Model):
    nome = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nome',
        help_text='Nome da bandeira.',
    )
    usar_debito = models.BooleanField(
        default=True,
        verbose_name='Usar débito',
        help_text='Indica se a bandeira poderá utilizar a modalidade de débito.',
    )
    usar_credito = models.BooleanField(
        default=True,
        verbose_name='Usar crédito',
        help_text='Indica se a bandeira poderá utilizar a modalidade de crédito.',
    )
    taxa_debito = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        default=None,
        verbose_name='Taxa a débito',
        help_text='Taxa a para pagamentos a débito.',
    )
    taxa_credito_avista = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        default=None,
        verbose_name='Taxa a crédito a vista',
        help_text='Taxa para pagamentos a crédito a vista.',
    )
    parcelar = models.BooleanField(
        default=False,
        verbose_name='Permitir parcelamento a crédito',
        help_text='Indica se será habilitada a opção de pagamento parcelado a crédito.',
    )
    taxa_6meses = models.BooleanField(
        default=False,
        verbose_name='Modo 6/6',
        help_text='Converte as taxas de crédito parcelado para taxas fixas para ' \
            '"até" e "acima de" 6 parcelas, respectivamente.'
    )
    parcelamento = models.SmallIntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(12)],
        null=True,
        blank=True,
        default=None,
        verbose_name='Quantidade de parcelas',
        help_text='Quantidade de parcelas permitidas para crédito.',
    )
    taxa_credito_parcelado = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        default=None,
        verbose_name='Taxa a crédito parcelado',
        help_text='Taxa para pagamentos a crédito parcelado.',
    )
    taxa_credito_parcelado_porparcela = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        default=None,
        verbose_name='Taxa a crédito parcelado, por parcela',
        help_text='Taxa a incidir sobre o número de parcelas do pagamento a crédito.'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Habilitar',
        help_text='Indica se a bandeira está ou não habilitada para uso.'
    )

    def __str__(self):
        ativo = (' [D]' if not self.ativo else '')
        return f'{self.nome}{ativo}'

    class Meta:
        verbose_name = 'Bandeira'
        verbose_name_plural = 'Bandeiras'
        ordering = ['nome', ]


class RegistrosCartoes(models.Model):
    DEBITO, CREDITO = 'DB', 'CR'
    OPERACAO_CHOICES = (
        (DEBITO, 'Débito'),
        (CREDITO, 'Crédito'),
    )

    data_registro = models.DateField(
        blank=True,
        default=timezone.now,
        verbose_name='Data do registro',
        help_text='Data em que foi adicionado o registro.',
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name='Usuário',
        help_text='Usuário que incluiu o registro.',
    )
    bandeira = models.ForeignKey(
        'api_cartoes.bandeiras',
        on_delete=models.PROTECT,
        verbose_name='Bandeira',
        help_text='Bandeira do cartão.',
    )
    operacao = models.CharField(
        max_length=2,
        choices=OPERACAO_CHOICES,
        verbose_name='Operação',
        help_text='Tipo de lançamento registrado.',
    )
    valor_servico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor do serviço',
        help_text='Valor do serviço registrado.',
    )
    valor_cobrado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Valor cobrado',
        help_text='Valor da cobrança (somados os juros ao valor do serviço).',
    )
    taxa_juros = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Taxa de juros',
        help_text='Taxa de juros aplicada à transação.',
    )
    parcelas = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name='Parcelas',
        help_text='Quantidade de parcelas (quando aplicável).'
    )
    protocolo = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        default=None,
        verbose_name='Protocolo',
        help_text='Protocolos relacionados ao registro.',
    )

    class Meta:
        verbose_name = "Registro"
        verbose_name_plural = "Registros"

    def __str__(self):
        return f'{self.data_registro} | {self.usuario} | R$ {self.valor_cobrado:.2f}'
