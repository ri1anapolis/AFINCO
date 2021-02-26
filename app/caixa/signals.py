# pylint: disable=missing-module-docstring,unused-argument
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.db.models import ProtectedError
from depositos.helper_functions import valores

from .models import LancamentoDeposito


@receiver(pre_save, sender=LancamentoDeposito, dispatch_uid="l_depositos_pre_save")
def depositos_pre_save(sender, instance, **kwargs):
    """Dispara ações após salvar um depósito no caixa."""

    if instance.id is None:
        dep_vlr_disponivel = valores(instance.deposito)["valor_disponivel"]

        if instance.id is None and float(instance.valor) > dep_vlr_disponivel:
            raise ProtectedError(
                f"O valor da operação (R$ {float(instance.valor)}) é maior que o valor disponível "
                f"no depósito (R$ {dep_vlr_disponivel})!",
                instance,
            )


@receiver(post_save, sender=LancamentoDeposito, dispatch_uid="l_depositos_post_save")
def depositos_post_save(sender, instance, **kwargs):
    """Dispara ações após salvar um depósito no caixa."""
    instance.deposito.save()


@receiver(post_delete, sender=LancamentoDeposito, dispatch_uid="l_depositos_post_del")
def depositos_post_delete(sender, instance, **kwargs):
    """Dispara ações após deletar um lançamento de depósito no caixa."""
    instance.deposito.save()
