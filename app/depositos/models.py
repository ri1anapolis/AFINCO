# pylint: disable=missing-module-docstring
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


class Depositos(models.Model):
    """Control de Depósitos Bancários"""

    data_deposito = models.DateField(
        verbose_name="Data",
        help_text="Data do depósito.",
    )
    valor = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor",
        help_text="Valor do depósito (em R$).",
    )
    valor_utilizado = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name="Valor Utilizado",
        help_text="Valor utilizado do depósito (em R$).",
        default=0,
        null=True,
        blank=True,
    )
    identificacao = models.CharField(
        verbose_name="Identificação",
        help_text="Identificação do depósito.",
        max_length=200,
    )
    observacoes = models.TextField(
        verbose_name="Observações",
        help_text="Anotações acerca do depósito.",
        max_length=600,
        null=True,
        blank=True,
    )
    data_add_reg = models.DateTimeField(
        verbose_name="Cadastrado em",
        help_text="Data do cadastro do depósito.",
        auto_now_add=True,
    )
    data_mod_reg = models.DateTimeField(
        verbose_name="Modificado em",
        help_text="Data da modificação do depósito.",
        auto_now=True,
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário",
        help_text="Último usuário a interagir com o depósito.",
    )
    consolidado = models.BooleanField(
        verbose_name="Consolidado",
        help_text="Define se o depósito pode ou não ser utilizado",
        default=False,
    )

    class Meta:
        verbose_name = "Depósito Bancário"
        verbose_name_plural = "Controle de Depósitos Bancários"
        ordering = [
            "-data_deposito",
            "-id",
            "identificacao",
            "valor",
        ]

    def __str__(self):
        consolidado = ""
        if self.consolidado:
            consolidado = " [C]"
        return (
            f"{self.data_deposito.strftime('%d/%m/%Y')} - {self.identificacao}"
            f" ( R$ {self.valor } ){consolidado}"
        )

    def get_absolute_url(self):
        """Retorna a URL absoluta para o depósito."""
        return reverse("deposito_detail", args=[str(self.id)])
