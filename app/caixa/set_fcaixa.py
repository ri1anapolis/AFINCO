# pylint: disable=missing-module-docstring,broad-except
import logging
from django.contrib import messages
from sentry_sdk import capture_exception
from depositos.helper_functions import consolidar
from .models import FechamentoCaixa

logger = logging.getLogger("afinco")


def consolida_depositos(f_caixa_id, usuario, request=None):
    """Chama consolidação sobre os depósitos relacionados ao fechamento de caixa."""
    success, alerta = True, None

    try:
        lancamentos_depositos_fcaixa = FechamentoCaixa.objects.get(
            id=f_caixa_id
        ).lancamentodeposito_set.select_related()
    except Exception as error:
        capture_exception(error)
        success = False
        alerta = f"[F001] Problema ao localizar os depósitos relacionados.\n\t{error}"
        logger.error("::: SALVAR FCAIXA|DEPÓSITOS|%s", alerta)
    else:
        if len(lancamentos_depositos_fcaixa) > 0:
            for lancamento_deposito in lancamentos_depositos_fcaixa:
                deposito = lancamento_deposito.deposito
                success, alerta = consolidar(deposito, usuario)

                if success and request:
                    messages.info(
                        request,
                        f'O depósito "{deposito}" foi consolidado ao consolidar o caixa!',
                    )

    return (success, alerta)
