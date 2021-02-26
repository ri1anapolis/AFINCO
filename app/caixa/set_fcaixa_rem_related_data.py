# pylint: disable=missing-module-docstring,broad-except,no-self-use
import logging
from sentry_sdk import capture_exception
from django.db import transaction
from clientes.models import ClienteServicos
from .models import LancamentoDeposito, Cheque, Comprovante

logger = logging.getLogger("afinco")


class RemoveRelatedDataFcaixa:
    """Remove dados relacionados ao fechamento de caixa"""

    @transaction.atomic
    def remove_depositos(self, depositos, f_caixa_id):
        """Remove depósitos do fechamento de caixa."""
        erro = ""

        for deposito in depositos:
            try:
                with transaction.atomic():
                    LancamentoDeposito.objects.get(
                        deposito_id=deposito,
                        fechamento_caixa_id=f_caixa_id,
                    ).delete()
            except Exception as error:
                capture_exception(error)
                erro = (
                    f"[E001A] Erro ao remover depósito(s) do banco de dados!\n\t{error}"
                )
                logger.error("::: SALVAR FCAIXA|DEPÓSITOS|%s", erro)
                break

        logger.info(
            "::: SALVAR FCAIXA|DEPÓSITOS|Removido(s) %s depósito(s) do fechamento de caixa.",
            len(depositos),
        )
        return erro

    @transaction.atomic
    def remove_cheques(self, cheques, f_caixa_id):
        """Remove cheques do fechamento de caixa."""
        erro = ""

        for cheque in cheques:
            try:
                with transaction.atomic():
                    Cheque.objects.get(
                        id=cheque,
                        fechamento_caixa_id=f_caixa_id,
                    ).delete()
            except Exception as error:
                capture_exception(error)
                erro = (
                    f"[E001B] Erro ao remover cheque(s) do banco de dados!\n\t{error}"
                )
                logger.error("::: SALVAR FCAIXA|CHEQUES|%s", erro)
                break

        logger.info(
            "::: SALVAR FCAIXA|CHEQUES|Removido(s) %s cheque(s) do fechamento de caixa.",
            len(cheques),
        )
        return erro

    @transaction.atomic
    def remove_comprovantes(self, comprovantes, f_caixa_id):
        """Remove comprovantes do fechamento de caixa."""
        erro = ""

        for comprovante in comprovantes:
            try:
                with transaction.atomic():
                    Comprovante.objects.get(
                        id=comprovante,
                        fechamento_caixa_id=f_caixa_id,
                    ).delete()
            except Exception as error:
                capture_exception(error)
                erro = f"[E001C] Erro ao remover comprovante(s) do banco de dados!\n\t{error}"
                logger.error("::: SALVAR FCAIXA|COMPROVANTES|%s", erro)
                break

        logger.info(
            "::: SALVAR FCAIXA|COMPROVANTES|Removido(s) %s comprovante(s) do fechamento de caixa.",
            len(comprovantes),
        )
        return erro

    @transaction.atomic
    def remove_clientes_servicos(self, servicos, f_caixa_id):
        """Remove serviços do fechamento de caixa."""
        erro = ""

        for servico in servicos:
            try:
                with transaction.atomic():
                    ClienteServicos.objects.get(
                        id=servico,
                        caixa_id=f_caixa_id,
                    ).delete()
            except Exception as error:
                capture_exception(error)
                erro = (
                    f"[E001D] Erro ao remover serviço(s) do banco de dados!\n\t{error}"
                )
                logger.error("::: SALVAR FCAIXA|SERVIÇOS|%s", erro)
                break

        return erro
