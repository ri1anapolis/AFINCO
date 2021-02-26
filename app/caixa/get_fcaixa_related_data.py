# pylint: disable=missing-module-docstring,pointless-string-statement
import logging
from sentry_sdk import capture_exception
from django.db.models import Q
from clientes.models import ClienteServicos
from .models import FechamentoCaixa, Cheque, LancamentoDeposito, Comprovante

logger = logging.getLogger("afinco")


def search_fcaixa(usuario_id=None, guiche_id=None, data=None, fcaixa_id=None):
    """Faz a busca pelos dados informados no banco de dados."""

    """O fornecimento das variáveis "data" e "fcaixa_id" são indicativos de que trata-se
    de uma busca, logo, faz-se uso delas pra tomada de decisão na forma da busca."""
    query = Q()

    if fcaixa_id is not None:
        query.add(Q(id=fcaixa_id), Q.AND)

    elif data is not None:
        query.add(Q(data=data), Q.AND)

        if guiche_id is not None:
            query.add(Q(guiche=guiche_id), Q.AND)
        if usuario_id is not None:
            query.add(Q(usuario=usuario_id), Q.AND)

    else:
        query.add(Q(usuario=usuario_id), Q.AND)
        query.add(Q(guiche=guiche_id), Q.AND)

    try:
        return FechamentoCaixa.objects.filter(query).order_by("-data").first()
    except Exception as error:  # pylint: disable=broad-except
        capture_exception(error)
        logger.error(
            "::: BUSCAR FCAIXA|BUSCA CAIXA|Erro ao buscar fechamento de caixa:\n\t%s",
            error,
        )
        raise Exception from error


def get_cheques(f_caixa_id):
    """Retorna os cheques relacionados ao fechamento de caixa"""
    obj_cheques = Cheque.objects.filter(fechamento_caixa=f_caixa_id)

    cheques = []
    for cheque in obj_cheques:
        cheques.append(
            {
                "id": cheque.id,
                "data": cheque.data,
                "banco": cheque.banco,
                "numero": cheque.numero,
                "emitente": cheque.emitente,
                "valor": float(cheque.valor),
            }
        )
    logger.info(
        "::: BUSCAR FCAIXA|CHEQUES|Relacionados(s) %s registro(s) ao fechamento de caixa.",
        len(cheques),
    )
    return cheques


def get_depositos(f_caixa_id):
    """Retorna os depósitos relacionados ao fechamento de caixa"""
    obj_depositos = LancamentoDeposito.objects.filter(fechamento_caixa=f_caixa_id)

    depositos = []
    for deposito in obj_depositos:
        depositos.append(
            {
                "id": deposito.deposito.id,
                "data_deposito": deposito.deposito.data_deposito,
                "valor_deposito": float(deposito.deposito.valor),
                "valor_utilizado": float(deposito.valor),
                "identificacao": deposito.deposito.identificacao,
                "observacoes": deposito.deposito.observacoes,
                "consolidado": deposito.deposito.consolidado,
            }
        )
    logger.info(
        "::: BUSCAR FCAIXA|DEPÓSITOS|Relacionados(s) %s registro(s) ao fechamento de caixa.",
        len(depositos),
    )
    return depositos


def get_comprovantes(f_caixa_id):
    """Retorna os comprovantes relacionados ao fechamento de caixa"""
    obj_comprovantes = Comprovante.objects.filter(fechamento_caixa=f_caixa_id)

    comprovantes = []
    for comprovante in obj_comprovantes:
        comprovantes.append(
            {
                "id": comprovante.id,
                "identificacao": comprovante.identificacao,
                "valor": float(comprovante.valor),
            }
        )
    logger.info(
        "::: BUSCAR FCAIXA|COMPROVANTES|Relacionados(s) %s registro(s) ao fechamento de caixa.",
        len(comprovantes),
    )
    return comprovantes


def get_clientes_servicos(f_caixa_id):
    """Recupera informações de serviços prestados a clientes cadastrados.
    Tais valores serão liquidados posteriormente, portanto o total desses
    valores é identificado como pagamento posterior."""
    obj_servicos = ClienteServicos.objects.filter(caixa=f_caixa_id)

    servicos = []
    for servico in obj_servicos:
        servicos.append(
            {
                "id": servico.id,
                "data_serv": servico.data,
                "cliente_id": servico.cliente.id,
                "cliente_nome": servico.cliente.nome,
                "tipo_protocolo": servico.tipo_protocolo,
                "protocolo": servico.protocolo,
                "valor": float(servico.valor),
                "observacoes": servico.observacoes,
                "liquidado": servico.liquidado,
            }
        )
    logger.info(
        "::: BUSCAR FCAIXA|SERVIÇOS|Relacionados(s) %s registro(s) ao fechamento de caixa.",
        len(servicos),
    )
    return servicos
