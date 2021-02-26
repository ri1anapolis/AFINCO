# pylint: disable=missing-module-docstring,broad-except,pointless-string-statement
import logging
from datetime import date
from escribadbquery.views import query_with_fetchall
from sentry_sdk import capture_exception
from django.db.models import Q
from clientes.models import Cliente

logger = logging.getLogger("afinco")


def get_valor_total_register(data, guiche_register):
    """Buscas e apresentação de fechamentos de caixas"""
    query_escriba = (
        "SELECT SUM(scx.cx_valor) AS Valor FROM sqlreg3.cx scx"
        " WHERE scx.cx_data = '{0}' AND scx.cx_guiche = '{1}'"
    )

    try:
        query = query_escriba.format(data, guiche_register)
        result_db = query_with_fetchall(query)
        logger.debug("::: REGISTER|VALOR TOTAL|Query ao banco de dados: %s", query)
        logger.debug("::: REGISTER|VALOR TOTAL|Retorno da query: %s", result_db)
    except Exception as error:
        capture_exception(error)
        logger.error("::: REGISTER|VALOR TOTAL|Erro ao buscar valor %s", error)
    else:
        if result_db[1] > 0 and result_db[0][0][0] is not None:
            valor_total = float(result_db[0][0][0])
            logger.info("::: REGISTER|VALOR TOTAL|Valor retornado: %s", valor_total)
            return valor_total

    return None


def get_cheques_register(data, guiche, cheques_existentes):
    """Busca no banco de dados cheques do register relacionados ao fechamento de caixa."""
    query_escriba = (
        "SELECT scx.Cx_DataCheque, sbc.Bc_Nome, scx.Cx_NumCheque, scx.cx_Nominal, scx.cx_valor"
        " FROM sqlreg3.cx scx LEFT JOIN sqlreg3.banco sbc ON (scx.Cx_Banco = sbc.Bc_Id)"
        " WHERE scx.cx_data = '{0}' AND scx.cx_guiche='{1}' AND scx.cx_formaPag = 'Cheque'"
        " AND scx.cx_valor > 0 AND scx.Cx_NumCheque IS NOT NULL AND scx.Cx_NumCheque <> ''"
    )

    try:
        query = query_escriba.format(data, guiche)
        result_db = query_with_fetchall(query)
        logger.debug("::: REGISTER|CHEQUES|Query ao banco de dados: %s", query)
        logger.debug("::: REGISTER|CHEQUES|Retorno da query: %s", result_db)
    except Exception as error:
        capture_exception(error)
        logger.error("::: REGISTER|CHEQUES|Erro ao buscar registros %s", error)
    else:
        logger.info(
            "::: REGISTER|CHEQUES|Retornado(s) %s registro(s) do Register.",
            result_db[1],
        )
        if result_db[1] > 0:
            return format_cheques_json(result_db[0], cheques_existentes)

    return []


def format_cheques_json(db_result, cheques):
    """Verifica os cheques recebidos do register e adiciona à relação
    de cheques do fechamento de caixa"""
    cheques_existentes = [] if cheques is None else cheques
    novos_cheques = []

    for row in db_result:
        cheque_ja_relacionado = False

        if len(cheques_existentes) > 0:
            for cheque in cheques_existentes:
                if cheque["banco"] == row[1] and cheque["numero"] == row[2]:
                    cheque_ja_relacionado = True
                    break

        if not cheque_ja_relacionado:
            unificado_fragmento_cheque = False
            if len(novos_cheques) > 0:
                for cheque in novos_cheques:
                    if cheque["banco"] == row[1] and cheque["numero"] == row[2]:
                        cheque["valor"] = cheque["valor"] + float(row[4])
                        unificado_fragmento_cheque = True
                        break

            if not unificado_fragmento_cheque:
                novos_cheques.append(
                    {
                        "id": None,
                        "data": row[0],
                        "banco": row[1],
                        "numero": row[2],
                        "emitente": row[3],
                        "valor": float(row[4]),
                    }
                )

    logger.info(
        "::: REGISTER|CHEQUES|Adicionado(s) %s registro(s) ao fechamento de caixa.",
        len(novos_cheques),
    )
    return novos_cheques


def get_servicos_clientes_register(
    guiche,
    data=date.today(),
    servicos=None,
    tipo_pagamento="Mensalista",
):
    """Busca por serviços de clientes no register"""

    if guiche:
        query_escriba = (
            "SELECT COALESCE(rc.Rc_Solicitante,rr.Rr_Apresentante) AS 'cliente_nome',"
            "REPLACE(REPLACE(REPLACE(COALESCE(rc.rc_CPFSolicitante,apr.ap_cpf),'.','')"
            ",'/',''),'-','') AS 'cliente_cpf',IF(cx.Cx_Tipo='Registro','RE',IF(cx.Cx_Tipo"
            "='Certidão','CE','EX')) AS 'tipo_protocolo',cx.cx_protocolo AS 'protocolo',"
            "cx.cx_data AS 'data',cx.cx_valor AS 'valor',cx.cx_obs AS 'observacoes',"
            "cx.cx_formaPag FROM sqlreg3.cx AS cx LEFT JOIN sqlreg3.rc AS rc ON (cx.Cx_Tipo"
            "='Certidão' AND cx.cx_protocolo=rc.rc_protocolo) LEFT JOIN sqlreg3.rr AS rr ON"
            "(cx.Cx_Tipo='Registro' AND cx.cx_protocolo=rr.Rr_Protocolo) LEFT JOIN "
            "sqlreg3.apresentante AS apr ON (rr.Rr_Apresentante=apr.Ap_Nome AND rr.Rr_EMail"
            "=apr.Ap_EMail) WHERE cx.cx_data='{0}' AND (rc.rc_CPFSolicitante IS NOT "
            "NULL OR apr.ap_cpf IS NOT NULL) AND cx.cx_guiche='{1}' AND cx.Cx_Tipo IN('Certidão',"
            "'Registro') AND cx.cx_valor > 0 AND cx.cx_formaPag='{2}'"
        )

        try:
            query = query_escriba.format(data, guiche, tipo_pagamento)
            result_db = query_with_fetchall(query)
            logger.debug("::: REGISTER|SERVIÇOS|Query ao banco de dados: %s", query)
            logger.debug("::: REGISTER|SERVIÇOS|Retorno da query: %s", result_db)
        except Exception as error:
            if error:
                capture_exception(error)
                logger.error("::: REGISTER|SERVIÇOS|Erro ao buscar registros %s", error)
        else:
            logger.info(
                "::: REGISTER|SERVIÇOS|Retornado(s) %s registro(s) do Register.",
                result_db[1],
            )
            if result_db[1] > 0:
                return format_servicos_clientes_json(result_db[0], servicos)

    return []


def format_servicos_clientes_json(db_result, servicos):
    """Procura por serviços no register e os retorna e json.
    Se informados serviços, será verificado se o register trouxe itens
    já existentes, nesses casos haverá deduplicação das informações.
    Este método retornará um novo dicionário no formato json com todos
    os serviços informados e recuperados do register.
    """
    servicos_existentes = servicos if servicos is not None else []
    novos_servicos = []
    clientes_saldos = {}

    for row in db_result:

        try:
            cliente_obj = (
                Cliente.objects.filter(
                    Q(cpf=row[1]) | Q(cnpj=row[1]) | Q(estrangeiro=row[1])
                )
                .exclude(ativo=False)
                .first()
            )
            if cliente_obj is None:
                raise Exception("Nenhum cliente retornado")
        except Exception:
            pass
        else:
            cliente = dict()
            servico_ja_relacionado = False

            for _attr in ("id", "nome", "verifica_saldo", "saldo"):
                cliente[_attr] = (
                    getattr(cliente_obj.outorgante, _attr)
                    if cliente_obj.outorgante
                    else getattr(cliente_obj, _attr)
                )

            if cliente["verifica_saldo"] and not clientes_saldos.get(cliente["id"]):
                clientes_saldos[cliente["id"]] = cliente["saldo"]

            for servico in servicos_existentes:
                if (
                    servico["cliente_id"] == cliente["id"]
                    and servico["tipo_protocolo"] == row[2]
                    and servico["protocolo"] == row[3]
                    and float(servico["valor"]) == float(row[5])
                ):
                    servico_ja_relacionado = True
                    break

            if not servico_ja_relacionado and clientes_saldos.get(
                cliente["id"], float(row[5])
            ) >= float(row[5]):
                """
                Somente relaciona o serviço se ele ainda não foi relacionado, ou,
                para os casos em que haja a necessidade de observar saldo, se o
                saldo for maior ou igual ao valor requerido!
                O valor de backup/default na testagem do saldo é para passar os
                serviços de clientes que não precisam verificar o saldo.
                """

                if clientes_saldos.get(cliente["id"]):
                    clientes_saldos[cliente["id"]] -= float(row[5])

                observacoes = (
                    f"::: Solicitado por {row[0]} ::: {observacoes}"
                    if cliente_obj.outorgante
                    else row[6]
                )

                novos_servicos.append(
                    {
                        "id": None,
                        "data_serv": row[4],
                        "cliente_id": cliente["id"],
                        "cliente_nome": cliente["nome"],
                        "tipo_protocolo": row[2],
                        "protocolo": row[3],
                        "valor": float(row[5]),
                        "observacoes": observacoes,
                        "liquidado": False,
                    }
                )

    logger.debug(
        "::: REGISTER|SERVIÇOS|Adicionado(s) o(s) registro(s):\n\t%s", novos_servicos
    )
    logger.info(
        "::: REGISTER|SERVIÇOS|Adicionado(s) %s registro(s) ao fechamento de caixa.",
        len(novos_servicos),
    )
    return novos_servicos
