# pylint: disable=missing-module-docstring
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from datetime import date


class Cliente(models.Model):
    """Cadastro de clientes"""

    CNPJ, CPF, ESTRANGEIRO = "PJ", "PF", "EX"
    DOCUMENTO_CHOICES = (
        (CPF, "CPF"),
        (CNPJ, "CNPJ"),
        (ESTRANGEIRO, "Estrangeiro"),
    )

    nome = models.CharField(
        max_length=200,
        verbose_name="Nome",
        help_text="Identificação do Cliente",
    )
    perfil = models.ForeignKey(
        "clientes.PerfilCliente",
        on_delete=models.SET_NULL,
        limit_choices_to={"ativo": True},
        null=True,
        blank=True,
        verbose_name="Perfil",
        help_text="Identificação do perfil de cliente.",
    )
    tipo_documento = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        choices=DOCUMENTO_CHOICES,
        verbose_name="Tipo de documento",
        help_text="Tipo de documento utilizado.",
    )
    cpf = models.CharField(
        null=True,
        blank=True,
        unique=True,
        default=None,
        max_length=14,
        verbose_name="CPF",
        help_text="Cadastro de Pessoa Física. (Somente dígitos)",
    )
    cnpj = models.CharField(
        null=True,
        blank=True,
        unique=True,
        default=None,
        max_length=18,
        verbose_name="CNPJ",
        help_text="Cadastro Nacional de Pessoa Jurídica. (Somente dígitos)",
    )
    estrangeiro = models.CharField(
        null=True,
        blank=True,
        unique=True,
        default=None,
        max_length=20,
        verbose_name="Documento Estrangeiro",
        help_text="Documento estrangeiro de identificação.",
    )
    telefone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Telefone",
        help_text="Telefone de contato.",
    )
    email = models.EmailField(
        max_length=254,
        null=True,
        blank=True,
        unique=True,
        verbose_name="E-mail",
        help_text="Endereço eletrônico do cliente.",
    )
    endereco = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name="Endereço",
        help_text="Endereço completo do cliente.",
    )
    outorgante = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Outorgante",
        help_text="Pessoa/Entidade que é representada por este cliente (quando aplicável).",
    )
    saldo_faturado = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name="Saldo Faturado",
        help_text="Saldo entre receitas e despesas das faturas.",
    )
    saldo = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name="Saldo",
        help_text="Saldo disponível na conta do cliente.",
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Está ativo?",
        help_text="Indica se o cliente pode ser utilizado.",
    )
    verifica_saldo = models.BooleanField(
        default=False,
        verbose_name="Verificação de Saldo",
        help_text="Somente serão lançados serviços ao cliente caso este"
        " possua saldo suficiente.",
    )

    def __str__(self):
        status = ""
        if not self.ativo:
            status += "[D]"
        if self.outorgante:
            status += "[O]"

        return f"{self.nome} {status}"

    def get_absolute_url(self):
        return reverse("cliente_detail", args=[str(self.id)])

    def clean(self):
        documentos = [self.cpf, self.cnpj, self.estrangeiro]
        for documento in documentos:
            if not documento:
                documento = None

    class Meta:
        ordering = ["-ativo", "nome"]


class PerfilCliente(models.Model):
    """Cadastro dos Perfils de clientes"""

    ANUAL, SEMANAL, QUINZENAL, MENSAL = "AN", "SE", "QE", "ME"
    BIMESTRAL, TRIMESTRAL, SEMESTRAL = "BM", "TM", "SM"
    PERIODO_PAG_CHOICES = (
        (SEMANAL, "Semanal"),
        (QUINZENAL, "Quinzenal"),
        (MENSAL, "Mensal"),
        (BIMESTRAL, "Bimestral"),
        (TRIMESTRAL, "Trimestral"),
        (SEMESTRAL, "Semestral"),
        (ANUAL, "Anual"),
    )

    nome = models.CharField(
        max_length=70,
        verbose_name="Perfil",
        help_text="Identificação do perfil de cliente.",
    )
    descricao = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Descrição",
        help_text="Descrição do perfil de cliente.",
    )
    periodo_pag = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        choices=PERIODO_PAG_CHOICES,
        verbose_name="Período de pagamento.",
        help_text="Perído de tempo para fechamento de fatura.",
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Está ativo?",
        help_text="Indica se o perfil de cliente pode ser utilizado.",
    )

    def __str__(self):
        status = ""
        if not self.ativo:
            status = " [D]"

        return f"{self.nome}{status}"

    def get_absolute_url(self):
        return reverse("perfil_cliente_detail", args=[str(self.id)])

    class Meta:
        verbose_name = "Perfil de Cliente"
        verbose_name_plural = "Perfís de Clientes"
        ordering = ["-ativo", "nome"]


class ClienteServicos(models.Model):
    """Cadastro dos serviços prestados ao cliente"""

    CERTIDAO, REGISTRO, EXAME = "CE", "RE", "EX"
    TIPO_PROT = (
        (CERTIDAO, "Certidão"),
        (REGISTRO, "Registro"),
        (EXAME, "Exame e Cálculo"),
    )

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        help_text="Cliente ao qual foi prestado o serviço.",
    )
    data = models.DateField(
        verbose_name="Data",
        help_text="Data em que foi prestado o serviço.",
    )
    tipo_protocolo = models.CharField(
        max_length=2,
        choices=TIPO_PROT,
        default=CERTIDAO,
        null=True,
        blank=True,
        verbose_name="Tipo de protocolo",
        help_text="Tipo do protocolo do register",
    )
    protocolo = models.PositiveIntegerField(
        validators=[MaxValueValidator(999999)],
        null=True,
        blank=True,
        verbose_name="Protocolo",
        help_text="Protocolo do serviço prestado no register.",
    )
    valor = models.FloatField(
        validators=[MinValueValidator(1)],
        verbose_name="Valor",
        help_text="Valor do serviço prestado.",
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        default="",
        verbose_name="Observações",
        help_text="Notas adicionais acerca do serviço.",
    )
    contabilizar = models.BooleanField(
        default=True,
        verbose_name="Contabilizar?",
        help_text="Indica se o serviço deve ser considerado para fins contábeis.",
    )
    liquidado = models.BooleanField(
        default=False,
        verbose_name="Liquidado?",
        help_text="Indica se o serviço já foi liquidado/pago.",
    )
    caixa = models.ForeignKey(
        "caixa.FechamentoCaixa",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Fechamento de Caixa",
        help_text="Indica em que fechamento de caixa foi realizado o serviço.",
    )
    fatura = models.ForeignKey(
        "clientes.ClienteFaturas",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        editable=False,
        verbose_name="Fatura",
        help_text="Indica a fatura à qual o serviço está relacionado.",
    )

    def __str__(self):
        status, prot = "", ""
        if self.liquidado:
            status = "[PG]"

        if not self.contabilizar:
            status += "[NC]"

        if self.caixa:
            status += "[CX]"

        if self.protocolo:
            prot = f", P:{self.tipo_protocolo}.{self.protocolo}"

        return (
            date.strftime(self.data, "%d/%m/%Y")
            + f' {str(self.cliente).split(" ", 1)[0]}{prot} '
            f"(R${self.valor}){status}"
        )

    def get_absolute_url(self):
        return reverse("cliente_servicos_detail", args=[str(self.id)])

    class Meta:
        verbose_name = "Serviço ao cliente"
        verbose_name_plural = "Serviços prestados ao Clientes"
        ordering = [
            "-data",
            "-id",
            "contabilizar",
            "liquidado",
            "-caixa",
            "cliente",
            "tipo_protocolo",
            "protocolo",
            "valor",
        ]


class ClienteFaturas(models.Model):
    DEPOSITO, DINHEIRO, CHEQUE = "DP", "DI", "CQ"
    FORMA_PAGAMENTO_CHOICES = (
        (DEPOSITO, "Depósito"),
        (DINHEIRO, "Dinheiro"),
        (CHEQUE, "Cheque"),
    )

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        help_text="Cliente da fatura.",
    )
    data_fatura = models.DateField(
        auto_now_add=True,
        verbose_name="Data da fatura",
        help_text="Data em que a fatura foi gerada.",
    )
    valor_servicos = models.FloatField(
        validators=[MinValueValidator(0)],
        blank=True,
        default=0,
        verbose_name="Valor dos serviços",
        help_text="Valor total dos serviços relacionados à fatura.",
    )
    valor_descontos = models.FloatField(
        validators=[MinValueValidator(0)],
        blank=True,
        default=0,
        verbose_name="Valor dos descontos",
        help_text="Valor total dos descontos incidentes sobre a fatura, quando houver.",
    )
    valor_fatura = models.FloatField(
        validators=[MinValueValidator(0)],
        blank=True,
        default=0,
        verbose_name="Valor da fatura",
        help_text="Valor total da fatura, observando-se os serviços e descontos.",
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Informações adicionais acerca da fatura.",
    )
    liquidado = models.BooleanField(
        default=False,
        verbose_name="Liquidado?",
        help_text="Indica se a fatura já foi ou não paga.",
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data do pagamento",
        help_text="Data do pagamento da fatura.",
    )

    class Meta:
        verbose_name = "Fatura de Serviços ao Cliente"
        verbose_name_plural = "Faturas de Serviços aos Clientes"
        ordering = [
            "-data_fatura",
            "-id",
            "liquidado",
            "cliente",
            "-data_pagamento",
        ]

    def __str__(self):
        return (
            f"{self.data_fatura.strftime('%d/%m/%Y')} - "
            f"{str(self.cliente).split(' ')[0]}... - R$ {self.valor_fatura}"
        )

    def get_absolute_url(self):
        return reverse("cliente_faturas_detail", args=[str(self.id)])


class ClientePagamentos(models.Model):
    DEPOSITO, DINHEIRO, CHEQUE = "DP", "DI", "CQ"
    FORMA_PAGAMENTO_CHOICES = (
        (DEPOSITO, "Depósito"),
        (DINHEIRO, "Dinheiro"),
        (CHEQUE, "Cheque"),
    )
    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.PROTECT,
        verbose_name="Cliente",
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        default=timezone.now,
        verbose_name="Data do pagamento",
        help_text="Data do pagamento.",
    )
    forma_pagamento = models.CharField(
        max_length=2,
        default=DINHEIRO,
        choices=FORMA_PAGAMENTO_CHOICES,
        verbose_name="Forma de pagamento",
    )
    valor = models.FloatField(
        validators=[MinValueValidator(0)],
        verbose_name="Valor",
        help_text="Valor do pagamento.",
    )
    deposito = models.ForeignKey(
        "depositos.Depositos",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Depósito",
        help_text="Identificação do depósito utilizado no pagamento.",
    )
    notas_adicionais = models.TextField(
        null=True,
        blank=True,
        verbose_name="Notas Adicionais",
        help_text="Informações adicionais acerca do pagamento.",
    )
    data_add = models.DateField(
        auto_now_add=True,
        verbose_name="Data da adição do registro.",
    )
    data_mod = models.DateField(
        auto_now=True,
        verbose_name="Data da modificação do registro.",
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
        help_text="Último usuário a interagir com o pagamento.",
    )

    class Meta:
        verbose_name = "Pagamento do Cliente"
        verbose_name_plural = "Pagamentos dos Clientes"
        ordering = [
            "-data_pagamento",
            "-id",
            "-data_add",
        ]

    def __str__(self):
        return (
            f"{self.data_pagamento.strftime('%d/%m/%Y')} - "
            f"{str(self.cliente).split(' ')[0]}... [R${self.valor}]"
        )

    def get_absolute_url(self):
        return reverse("cliente_pagamentos_detail", args=[str(self.id)])
