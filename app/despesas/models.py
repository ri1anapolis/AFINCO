from django.db import models
from django.urls import reverse


class CategoriaDespesa(models.Model):
    codigo_rf = models.PositiveIntegerField(
        verbose_name='Código',
        help_text='Código da despesa conforme tabela da Receita Federal.',
        unique=True,
    )
    conta_credito = models.PositiveIntegerField(
        verbose_name='Conta de Crédito',
        help_text='Conta onde será creditado o valor.',
        null=True,
        blank=True,
    )
    conta_debito = models.PositiveIntegerField(
        verbose_name='Conta de Débito',
        help_text='Conta onde será debitado o valor.',
        null=True,
        blank=True,
    )
    identificacao = models.CharField(
        verbose_name='Descrição',
        help_text='Discriminação do tipo de despesa.',
        max_length=200,
    )
    ativo = models.BooleanField(
        verbose_name='Está ativo?',
        help_text='Indica se o tipo de despesa está ativo e pode ser utilizado.',
        default=True,
    )
    relatorios = models.BooleanField(
        verbose_name='Relatório?',
        help_text='Indica se as despesas dessa categoria podem ser consideradas pelos relatórios.',
        default=True,
    )

    class Meta:
        verbose_name = 'Categoria de Despesa'
        verbose_name_plural = 'Categorias de Despesas'
        ordering = ['-ativo', 'identificacao', 'codigo_rf', ]

    def __str__(self):
        ativo = ''
        if not self.ativo:
            ativo = ' - [Inativo]'
        return f'#{self.codigo_rf}, {self.identificacao}{ativo}'
    
    def get_absolute_url(self):
        return reverse("categoria_despesa_detail", args=[str(self.pk)])
    


class Despesa(models.Model):
    """Cadastro de Despesas"""

    data_despesa = models.DateField(
        verbose_name='Data',
        help_text='Data da despesa.',
    )
    identificacao = models.ForeignKey(
        'despesas.HistoricosDespesas',
        on_delete=models.PROTECT,
        verbose_name='Histórico',
        help_text='Descrição da despesa.',
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor',
        help_text='Valor da despesa.',
    )
    categoria_despesa = models.ForeignKey(
        'despesas.CategoriaDespesa',
        on_delete=models.PROTECT,
        verbose_name='Categoria',
        help_text='Categoria da despesa conforme tabela da Receita Federal.',
    )
    observacoes = models.TextField(
        verbose_name='Observações',
        help_text='Observações acerca da despesa.',
        null=True,
        blank=True,
    )
    contabilizar_cofre = models.BooleanField(
        verbose_name='Contabilizar no Cofre?',
        help_text='Indica se a despesa deve ser descontada do saldo do cofre, quando vinculada.',
        default=False,
    )

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_despesa', '-id', ]

    def __str__(self):
        return f'{self.identificacao.identificacao[:32]} ( R$ {self.valor} )'

    def get_absolute_url(self):
        return reverse("despesa_detail", kwargs={"pk": self.pk})


class HistoricosDespesas(models.Model):
    """Cadastro de históricos mais usados pelas despesas."""
    identificacao = models.CharField(
        max_length=250,
        verbose_name='Histórico',
        help_text='Descrição da despesa.',
    )

    class Meta:
        verbose_name = 'Histórico'
        verbose_name_plural = 'Históricos de Despesas'
        ordering = ['identificacao', ]

    def __str__(self):
        return f'{self.identificacao}'
