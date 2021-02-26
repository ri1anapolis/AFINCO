from django.db import models


class Guiche(models.Model):
    """Guichês"""
    nome = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Nome',
        help_text='Nome do guichê.'
    )
    descricao = models.CharField(
        max_length=400,
        null=True,
        blank=True,
        verbose_name='Descrição',
        help_text='Descrição do guichê.'
    )
    id_register = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name='ID Register',
        help_text='ID do guichê no Register.'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text='Indica se o guichê está ativo ou não.'
    )

    def __str__(self):
        return str(self.nome)

    class Meta:
        verbose_name = 'Guichê'
        verbose_name_plural = 'Guichês'
        ordering = ['nome']
