# pylint: disable=missing-module-docstring
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class Cheque(models.Model):
    """Model para arquivamento de cheques"""

    banco = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Banco",
        help_text="Banco do cheque.",
    )
    numero = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Número do cheque",
        help_text="Número do cheque.",
    )
    data = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data",
        help_text="Data do cheque.",
    )
    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor",
        help_text="Valor do cheque.",
    )
    emitente = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Emitente",
        help_text="Identificação de quem emitiu o cheque.",
    )
    fechamento_caixa = models.ForeignKey(
        "caixa.FechamentoCaixa",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Fechamento de caixa",
        help_text="Fechamento de caixa no qual o cheque foi utilizado.",
    )

    def __str__(self):
        return f"{self.numero} {self.banco}"


class Comprovante(models.Model):
    """Model para arquivamento de Comprovantes"""

    identificacao = models.CharField(
        max_length=200,
        verbose_name="Comprovantes",
        help_text="Comprovantes de pagamentos.",
    )
    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor",
        help_text="Valor do documento.",
    )
    fechamento_caixa = models.ForeignKey(
        "caixa.FechamentoCaixa",
        on_delete=models.CASCADE,
        verbose_name="Fechamento de caixa",
        help_text="Fechamento de caixa no qual o comprovante foi utilizado.",
    )

    def __str__(self):
        return f"{self.identificacao} ( {self.valor} )"


class LancamentoDeposito(models.Model):
    """Model M:M do relacionamento entre depositos e fechamento de caixa LancamentoDeposito"""

    fechamento_caixa = models.ForeignKey(
        "caixa.FechamentoCaixa",
        on_delete=models.PROTECT,
        verbose_name="Fechamento de caixa",
        help_text="Fechamento de caixa relacionado.",
    )
    deposito = models.ForeignKey(
        "depositos.Depositos",
        on_delete=models.PROTECT,
        verbose_name="Depósito",
        help_text="Depósito bancário relacionado.",
    )
    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor",
        help_text="Valor do depósito usado no fechamento de caixa.",
    )

    class Meta:
        verbose_name = "Lançamento de Depósito"
        verbose_name_plural = "Lançamento de Depósitos"
        unique_together = ("fechamento_caixa", "deposito")

    def __str__(self):
        return f"Utilizado R$ {self.valor} em: {self.fechamento_caixa}"


class FechamentoCaixa(models.Model):
    """Model para armazenamento de informações de Fechamento de Caixa"""

    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        verbose_name="Usuário",
        help_text="Usuário responsável pelo fechamento de caixa.",
    )
    guiche = models.ForeignKey(
        "guiches.Guiche",
        on_delete=models.PROTECT,
        verbose_name="Guichê",
        help_text="Guichê do fechamento de caixa.",
    )
    data = models.DateField(
        verbose_name="Data",
        help_text="Data do fechamento de caixa.",
    )
    saldo_inicial = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Saldo Inicial",
        help_text="Valor pre-existente no caixa.",
    )
    valor_dinheiro_caixa = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Dinheiro em caixa",
        help_text="Valor do caixa em dinheiro.",
    )
    valor_dinheiro_cofre = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Dinheiro para o cofre",
        help_text="Valor em dinheiro enviado ao cofre.",
    )
    valor_depositos = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor em Depósitos",
        help_text="Valor total do caixa em depósitos (enviado ao cofre).",
    )
    valor_cheques = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor em Cheques",
        help_text="Valor total do caixa em cheques (enviado ao cofre).",
    )
    valor_comprovantes = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor em Comprovantes",
        help_text="Valor total do caixa em comprovantes (enviado ao cofre).",
    )
    valor_cartoes = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor em Cartões",
        help_text="Valor total do caixa pago em cartões (compõe o valor em comprovantes).",
    )
    valor_total_servicos_clientes = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor em Pagamentos Posteriores",
        help_text="Valor total dos pagamentos posteriores.",
    )
    valor_desp_futuras = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor de Despesas Futuras",
        help_text="Valor total dos valores a serem utilizados para despesas posteriores.",
    )
    valor_total_entrada = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor Total de Entrada",
        help_text="Valor total dos valores que entraram no caixa.",
    )
    valor_quebra = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor Quebra de Caixa",
        help_text="Valor da diferença entre o fechamento de caixa e o caixa do register.",
    )
    valor_total = models.DecimalField(
        default=0,
        max_digits=20,
        decimal_places=2,
        null=True,
        verbose_name="Valor Total Geral",
        help_text="Valor total do fechamento de caixa.",
    )
    depositos = models.ManyToManyField(
        "depositos.Depositos",
        through="caixa.LancamentoDeposito",
    )
    fechado = models.BooleanField(
        default=False,
        verbose_name="Entregar Fechamento",
        help_text=(
            "Indica se o fechamento de caixa já pode ser "
            "enviado para análise do setor financeiro."
        ),
    )
    consolidado = models.BooleanField(
        default=False,
        verbose_name="Consolidado",
        help_text="Indica se o valor foi consolidado pelo setor financeiro.",
    )
    qtd_devolucoes = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Devoluções",
        help_text="Quantidade de devoluções efetuadas até o fechamento do caixa.",
    )
    observacoes = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name="Observações",
        help_text="Observações acerca do fechamento de caixa.",
    )
    qtd_moeda_01cent = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 0,01",
        help_text="Quantidade de moedas de R$ 0,01.",
    )
    qtd_moeda_05cent = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 0,05",
        help_text="Quantidade de moedas de R$ 0,05.",
    )
    qtd_moeda_10cent = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 0,10",
        help_text="Quantidade de moedas de R$ 0,10.",
    )
    qtd_moeda_25cent = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 0,25",
        help_text="Quantidade de moedas de R$ 0,25.",
    )
    qtd_moeda_50cent = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 0,50",
        help_text="Quantidade de moedas de R$ 0,50.",
    )
    qtd_moeda_01real = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 1,00",
        help_text="Quantidade de moedas de R$ 1,00.",
    )
    qtd_moeda_02reais = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 2,00",
        help_text="Quantidade de moedas de R$ 2,00.",
    )
    qtd_moeda_05reais = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 5,00",
        help_text="Quantidade de moedas de R$ 5,00.",
    )
    qtd_moeda_10reais = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 10,00",
        help_text="Quantidade de moedas de R$ 10,00.",
    )
    qtd_moeda_20reais = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 20,00",
        help_text="Quantidade de moedas de R$ 20,00.",
    )
    qtd_moeda_50reais = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 50,00",
        help_text="Quantidade de moedas de R$ 50,00.",
    )
    qtd_moeda_100reais = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="R$ 100,00",
        help_text="Quantidade de moedas de R$ 100,00.",
    )
    data_mod_reg = models.DateTimeField(
        verbose_name="Modificado em",
        help_text="Data da modificação do fechamento de caixa.",
        editable=False,
        blank=True,
    )
    historico = models.TextField(
        verbose_name="Histórico",
        help_text="Histórico de ações no registro do fechamento de caixa.",
        editable=False,
        null=True,
    )
    usuario_mod = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
        related_name="usuario_mod",
        verbose_name="Usuário",
        help_text="Último usuário a interagir com o depósito.",
    )

    def __str__(self):
        return (
            f"{self.data.strftime('%d/%m/%Y')} - {self.guiche}"
            f" / {self.usuario} / Total: R$ {self.valor_total}"
        )

    def save(self, *args, **kwargs):
        self.data_mod_reg = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Fechamento de Caixa"
        ordering = ["-data"]
        unique_together = ("usuario", "data")


class ConfiguracaoCaixa(models.Model):
    """Configurações relativas aos caixas"""

    descricao = models.CharField(
        max_length=120,
        unique=True,
        verbose_name="Descrição",
        help_text="Descritivo da configuração",
    )
    usuarios = models.ManyToManyField(
        get_user_model(),
        verbose_name="Usuários",
        help_text="Usuários aos quais se aplica a configuração de caixa.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo?",
        help_text="Indica se a configuração está ou não ativa.",
    )
    precedencia = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name="Precedência",
        help_text="O valor da precedência é usado para tomada de decisões acerca da\
            configuração a ser usada. (Ordem crescente)",
    )
    qtd_moeda_01cent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 0,01",
        help_text="Quantidade de moedas de R$ 0,01.",
    )
    qtd_moeda_05cent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 0,05",
        help_text="Quantidade de moedas de R$ 0,05.",
    )
    qtd_moeda_10cent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 0,10",
        help_text="Quantidade de moedas de R$ 0,10.",
    )
    qtd_moeda_25cent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 0,25",
        help_text="Quantidade de moedas de R$ 0,25.",
    )
    qtd_moeda_50cent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 0,50",
        help_text="Quantidade de moedas de R$ 0,50.",
    )
    qtd_moeda_01real = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 1,00",
        help_text="Quantidade de moedas de R$ 1,00.",
    )
    qtd_moeda_02reais = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 2,00",
        help_text="Quantidade de moedas de R$ 2,00.",
    )
    qtd_moeda_05reais = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 5,00",
        help_text="Quantidade de moedas de R$ 5,00.",
    )
    qtd_moeda_10reais = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 10,00",
        help_text="Quantidade de moedas de R$ 10,00.",
    )
    qtd_moeda_20reais = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 20,00",
        help_text="Quantidade de moedas de R$ 20,00.",
    )
    qtd_moeda_50reais = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 50,00",
        help_text="Quantidade de moedas de R$ 50,00.",
    )
    qtd_moeda_100reais = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="R$ 100,00",
        help_text="Quantidade de moedas de R$ 100,00.",
    )

    class Meta:
        verbose_name = "Configuração de Caixa"
        verbose_name_plural = "Configurações de Caixas"

    def __str__(self):
        return f"{self.descricao}"
