# pylint: disable=missing-module-docstring
import logging
from django.db.models import ProtectedError, Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from sentry_sdk import capture_exception

from .models import Depositos

logger = logging.getLogger("afinco")


def calc_valor_utilizado(deposito):
    """Retorna o objeto de depósito a partir da PK fornecida."""

    try:
        valor_caixas = (
            deposito.lancamentodeposito_set.select_related().aggregate(Sum("valor"))[
                "valor__sum"
            ]
        ) or 0

        valor_cliente_pagamentos = (
            deposito.clientepagamentos_set.select_related().aggregate(Sum("valor"))[
                "valor__sum"
            ]
        ) or 0

        return float(valor_caixas) + float(valor_cliente_pagamentos)

    except Exception as error:  # pylint: disable=broad-except
        capture_exception(error)
        logger.error(
            "::: DEPÓSITOS|CÁLCULO|Erro ao calcular valor utilizado\n\t%s", error
        )
        return str(error)


@receiver(pre_save, sender=Depositos)
def depositos_pre_save(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """Dispara ações após salvar um depósito."""

    valor_utilizado = calc_valor_utilizado(instance)

    if isinstance(valor_utilizado, (float, int)):
        if valor_utilizado > float(instance.valor):
            raise ProtectedError(
                "O depósito não pode ser salvo pois o valor indicado não está disponível!",
                instance,
            )

        instance.valor_utilizado = valor_utilizado

    else:
        raise ProtectedError(
            f"O depósito não pode ser salvo devido ao erro: {valor_utilizado}",
            instance,
        )
