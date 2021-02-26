# pylint: disable=missing-module-docstring
import logging
from sentry_sdk import capture_exception

from .models import Depositos

logger = logging.getLogger("afinco")


def get_deposito_object(deposito):
    """Return object from given PK."""
    try:
        if isinstance(deposito, Depositos):
            """
            refresh_from_db() atualiza os valores sobre o objeto existente
            e retorna None como resultado. Devido a esse comportamento não
            pode ser retornado diretamente e, portanto, executado e só então
            retornado!
            """  # pylint: disable=pointless-string-statement
            deposito.refresh_from_db()
            return deposito

        return Depositos.objects.get(id=deposito)

    except Exception as error:  # pylint: disable=broad-except
        capture_exception(error)
        logger.erro("DEPÓSITO|Erro ao buscar depósito: %s", error)
        return str(error)


def valores(deposito_obj_or_pk):
    """Retorna o valor de depósito, o valor utiliza e o valor disponível."""
    deposito = get_deposito_object(deposito_obj_or_pk)
    if isinstance(deposito, Depositos):
        return {
            "valor_deposito": float(deposito.valor),
            "valor_utilizado": float(deposito.valor_utilizado),
            "valor_disponivel": float(deposito.valor) - float(deposito.valor_utilizado),
        }
    return deposito


def consolidavel(deposito_obj_or_pk):
    """Indica se o depósito é passível de consolidação"""
    deposito = get_deposito_object(deposito_obj_or_pk)
    if not isinstance(deposito, str):
        fcaixa_objects = list(deposito.lancamentodeposito_set.select_related())
        fcaixas_consolidados = [
            lcaixa.fechamento_caixa.consolidado for lcaixa in fcaixa_objects
        ]

        if (
            valores(deposito)["valor_disponivel"] < 2
            and not deposito.consolidado
            and all(fcaixas_consolidados)
        ):
            return True

    return False


def consolidar(deposito_obj_or_pk, usuario_obj=None):
    """Consolida o depósito, se possível"""
    deposito = get_deposito_object(deposito_obj_or_pk)
    if not isinstance(deposito, str) and consolidavel(deposito):
        try:
            deposito.consolidado = True
            deposito.usuario = usuario_obj
            deposito.save()
            return True, None

        except Exception as error:  # pylint: disable=broad-except
            return (
                False,
                f"Houve um erro ao tentar consolidadar o depósito: {error}",
            )

    else:
        return False, "O depósito não atende os requisitos para consolidação!"
