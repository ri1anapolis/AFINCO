# pylint: disable=missing-module-docstring,missing-function-docstring,unused-argument,broad-except
import logging
from django.db.models import ProtectedError
from django.db.models.signals import pre_delete, post_delete, post_save
from django.dispatch import receiver
from sentry_sdk import capture_exception, capture_message

from depositos.helper_functions import consolidar
from .models import ClienteServicos, ClienteFaturas, ClientePagamentos
from .views import ClienteConta

logger = logging.getLogger("afinco")


def saldo_faturado_cliente(instance):
    """Atualiza o saldo faturado do cliente."""
    _saldo_faturado = ClienteConta().saldo_faturado(instance.cliente)

    try:
        if _saldo_faturado is not None:
            instance.cliente.saldo_faturado = _saldo_faturado
            instance.cliente.save()

            if getattr(instance, "deposito", False):
                instance.deposito.save()
                consolidar(instance.deposito)

        else:
            raise Exception("Não há saldo faturado existente para o cliente")

    except Exception as error:
        msg = f"Não foi possível atualizar o saldo faturado ({_saldo_faturado}) do cliente."
        capture_exception(error)
        capture_message(msg)
        logger.error("::: FATURAS DE CLIENTES|SALDO FATURADO|%s", error)
        raise Exception(msg, instance) from error
    else:
        saldo_liquido_cliente(instance)


def saldo_liquido_cliente(instance):
    """Atualiza o saldo liquido do cliente."""
    _saldo_liquido = ClienteConta().saldo_liquido(instance.cliente)

    try:
        if _saldo_liquido is not None:
            instance.cliente.saldo = _saldo_liquido
            instance.cliente.save()

        else:
            raise Exception

    except Exception as error:
        msg = f"Não foi possível atualizar o saldo liquido ({_saldo_liquido}) do cliente: {error}"
        capture_exception(error)
        capture_message(msg)
        raise Exception(msg, instance) from error


#
#  SERVIÇOS DE CLIENTES


@receiver(pre_delete, sender=ClienteServicos)
def cliente_servicos_pre_delete(sender, instance, **kwargs):

    if getattr(instance, "caixa", False) and (
        instance.caixa.fechado or instance.caixa.consolidado
    ):
        raise ProtectedError(
            "O serviço não pode ser removido devido a estar vinculado "
            f'ao fechamento de caixa "{instance.caixa}"!',
            instance,
        )

    if getattr(instance, "fatura", False):
        raise ProtectedError(
            "O serviço não pode ser removido devido a estar vinculado "
            f'à fatura "{instance.fatura}"!',
            instance,
        )


@receiver(post_delete, sender=ClienteServicos)
def cliente_servicos_post_delete(sender, instance, **kwargs):
    saldo_liquido_cliente(instance)


@receiver(post_save, sender=ClienteServicos)
def cliente_servicos_post_save(sender, instance, **kwargs):
    saldo_liquido_cliente(instance)


#
# FATURAS DE CLIENTES


@receiver(post_delete, sender=ClienteFaturas)
def cliente_faturas_post_delete(sender, instance, **kwargs):
    saldo_faturado_cliente(instance)


@receiver(post_save, sender=ClienteFaturas, dispatch_uid="cliente_faturas_post_save")
def cliente_faturas_post_save(sender, instance, **kwargs):
    saldo_faturado_cliente(instance)

    if getattr(instance, "clienteservicos_set"):
        servicos = instance.clienteservicos_set.select_related()
        for servico in servicos:
            try:
                servico.liquidado = instance.liquidado
                servico.save()
            except Exception as error:
                capture_exception(error)
                logger.error(
                    "::: FATURAS DE CLIENTES|LIQUIDAR SERVIÇOS RELACIONADOS|%s", error
                )


#
#  PAGAMENTOS DE CLIENTES


@receiver(pre_delete, sender=ClientePagamentos)
def cliente_pagamentos_pre_delete(sender, instance, **kwargs):

    if getattr(instance.deposito, "consolidado", False):
        raise ProtectedError(
            "O pagamento não pode ser removido pois está vinculado "
            f'ao depósito consolidado "{instance.deposito}"!',
            instance,
        )


@receiver(post_delete, sender=ClientePagamentos)
def cliente_pagamentos_post_delete(sender, instance, **kwargs):
    saldo_faturado_cliente(instance)


@receiver(post_save, sender=ClientePagamentos)
def cliente_pagamentos_post_save(sender, instance, **kwargs):
    saldo_faturado_cliente(instance)
