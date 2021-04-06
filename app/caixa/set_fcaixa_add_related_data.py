# pylint: disable=missing-module-docstring,broad-except,no-self-use
import logging
from datetime import date
from sentry_sdk import capture_exception
from django.db import transaction
from django.db.models import Q
from clientes.views import ClienteConta
from clientes.models import ClienteServicos, Cliente
from depositos.models import Depositos
from .models import LancamentoDeposito, Cheque, Comprovante
from .fcaixa_helper_functions import valid_dict_value

logger = logging.getLogger("afinco")


class SaveRelatedDataFcaixa:
    """Salva dados relacionados ao fechamento de caixa"""

    @transaction.atomic
    def save_depositos(self, depositos, f_caixa_id):
        """Salva os novos depósito recebidos do cliente."""
        depositos_ids_client, erro = [], ""

        for deposito in depositos:
            obj_lanc_deposito = LancamentoDeposito.objects.filter(
                deposito_id=deposito["id"],
                fechamento_caixa_id=f_caixa_id,
            )
            if obj_lanc_deposito.count() < 1:
                try:
                    with transaction.atomic():
                        obj_deposito = Depositos.objects.get(id=deposito["id"])
                        obj_lanc_deposito = LancamentoDeposito.objects.create(
                            fechamento_caixa_id=f_caixa_id,
                            deposito_id=obj_deposito.id,
                            valor=deposito["valor_utilizado"],
                        )
                        obj_lanc_deposito.save()

                except Exception as error:
                    capture_exception(error)
                    depositos_ids_client = []
                    erro = (
                        f"[D001A] Houve um erro ao tentar vincular depositos!\n{error}"
                    )
                    logger.error("::: SALVAR FCAIXA|DEPÓSITOS|%s", erro)
                    break
                else:
                    depositos_ids_client.append(
                        {
                            "local_id": deposito["local_id"],
                            "id": obj_lanc_deposito.deposito_id,
                        }
                    )

        logger.info(
            "::: SALVAR FCAIXA|DEPÓSITOS|Salvo(s) %s registros(s) no fechamento de caixa.",
            len(depositos_ids_client),
        )
        return (depositos_ids_client, erro)

    @transaction.atomic
    def save_cheques(self, cheques, f_caixa_id):
        """Salva os novos cheques recebidos do cliente."""
        cheques_ids_client, erro = [], ""

        for cheque in cheques:
            cheques_salvos = Cheque.objects.filter(
                Q(id=cheque.get("id"))
                | (
                    Q(numero=cheque.get("numero"))
                    & Q(valor=cheque.get("valor"))
                    & Q(fechamento_caixa_id=f_caixa_id)
                )
            )

            if cheques_salvos.count() < 1:
                try:
                    with transaction.atomic():
                        novo_cheque = Cheque.objects.create(
                            fechamento_caixa_id=f_caixa_id,
                            banco=cheque["banco"],
                            numero=cheque["numero"],
                            data=cheque["data"],
                            valor=cheque["valor"],
                            emitente=cheque["emitente"],
                        )
                        novo_cheque.save()

                except Exception as error:
                    capture_exception(error)
                    cheques_ids_client = []
                    erro = f"[D001B] Houve um erro ao tentar vincular cheques!\n{error}"
                    logger.error("::: SALVAR FCAIXA|CHEQUES|%s", erro)
                    break
                else:
                    cheques_ids_client.append(
                        {
                            "local_id": cheque["local_id"],
                            "id": novo_cheque.id,
                        }
                    )

        logger.info(
            "::: SALVAR FCAIXA|CHEQUES|Salvo(s) %s registros(s) no fechamento de caixa.",
            len(cheques_ids_client),
        )
        return (cheques_ids_client, erro)

    @transaction.atomic
    def save_comprovantes(self, comprovantes, f_caixa_id):
        """Salva os novos comprovantes recebidos do cliente."""
        comprovantes_ids_client, erro = [], ""

        for comprovante in comprovantes:
            comprovantes_salvos = Comprovante.objects.filter(
                Q(id=comprovante.get("id"))
                | (
                    Q(identificacao=comprovante.get("identificacao"))
                    & Q(valor=comprovante.get("valor"))
                    & Q(fechamento_caixa_id=f_caixa_id)
                )
            )

            if comprovantes_salvos.count() < 1:
                try:
                    with transaction.atomic():
                        obj_lanc_comprovante = Comprovante.objects.create(
                            fechamento_caixa_id=f_caixa_id,
                            identificacao=comprovante["identificacao"],
                            valor=comprovante["valor"],
                        )
                        obj_lanc_comprovante.save()

                except Exception as error:
                    capture_exception(error)
                    comprovantes_ids_client = []
                    erro = f"[D001C] Houve um erro ao tentar vincular comprovantes!\n{error}"
                    logger.error("::: SALVAR FCAIXA|COMPROVANTES|%s", erro)
                    break
                else:
                    comprovantes_ids_client.append(
                        {
                            "local_id": comprovante["local_id"],
                            "id": obj_lanc_comprovante.id,
                        }
                    )

        logger.info(
            "::: SALVAR FCAIXA|COMPROVANTES|Salvo(s) %s registros(s) no fechamento de caixa.",
            len(comprovantes_ids_client),
        )
        return (comprovantes_ids_client, erro)

    @transaction.atomic
    def save_clientes_servicos(self, servicos, f_caixa_id, data=None):
        """ Salva os serviço realizados no caixa."""
        data = data or date.today()

        """Salva os novos serviços recebidos do cliente."""  # pylint: disable=pointless-string-statement
        clientes_servicos_ids, erro = [], ""

        for servico in servicos:
            servicos_salvos = ClienteServicos.objects.filter(
                cliente_id=servico.get("cliente_id"),
                caixa_id=f_caixa_id,
                valor=servico.get("valor"),
                tipo_protocolo=servico.get("tipo_protocolo"),
                protocolo=servico.get("protocolo"),
            )

            if servicos_salvos.count() < 1:
                try:
                    with transaction.atomic():
                        if not ClienteConta().test_valor(
                            servico["cliente_id"], servico["valor"]
                        ):
                            raise Exception(
                                f'\n\t[D001DBA] O cliente "{servico["cliente_nome"]}"'
                                "pode não ter saldo suficiente para receber mais serviços!"
                            )

                        cliente = Cliente.objects.get(id=servico["cliente_id"])
                        novos_servicos = ClienteServicos.objects.create(
                            caixa_id=f_caixa_id,
                            cliente_id=cliente.id,
                            valor=servico["valor"],
                            tipo_protocolo=servico["tipo_protocolo"],
                            protocolo=servico["protocolo"],
                            observacoes=servico.get("observacoes", ""),
                            data=data,
                        )
                        novos_servicos.save()

                except Exception as erro:
                    capture_exception(erro)
                    clientes_servicos_ids = []
                    erro = "[D001DB] Houve um erro ao tentar vincular o serviço ao cliente!{erro}"
                    logger.error("::: SALVAR FCAIXA|COMPROVANTES|%s", erro)
                    break
                else:
                    clientes_servicos_ids.append(
                        {
                            "local_id": servico["local_id"],
                            "id": novos_servicos.id,
                        }
                    )

        logger.info(
            "::: SALVAR FCAIXA|SERVIÇOS|Salvo(s) %s registros(s) no fechamento de caixa.",
            len(clientes_servicos_ids),
        )
        return (clientes_servicos_ids, erro)

    @transaction.atomic
    def save_valores(self, post_data, f_caixa):
        """Salva os valores gerais do fechamente de caixa."""
        erro = ""
        valores_array = [
            {"key": "saldo_inicial", "type": "float", "default": 0},
            {"key": "valor_dinheiro_caixa", "type": "float", "default": 0},
            {"key": "valor_dinheiro_cofre", "type": "float", "default": 0},
            {"key": "valor_depositos", "type": "float", "default": 0},
            {"key": "valor_total_servicos_clientes", "type": "float", "default": 0},
            {"key": "valor_cheques", "type": "float", "default": 0},
            {"key": "valor_comprovantes", "type": "float", "default": 0},
            {"key": "valor_cartoes", "type": "float", "default": 0},
            {"key": "valor_desp_futuras", "type": "float", "default": 0},
            {"key": "valor_total_entrada", "type": "float", "default": 0},
            {"key": "valor_quebra", "type": "float", "default": 0},
            {"key": "valor_total", "type": "float", "default": 0},
            {"key": "qtd_moeda_01cent", "type": "int", "default": 0},
            {"key": "qtd_moeda_05cent", "type": "int", "default": 0},
            {"key": "qtd_moeda_10cent", "type": "int", "default": 0},
            {"key": "qtd_moeda_25cent", "type": "int", "default": 0},
            {"key": "qtd_moeda_50cent", "type": "int", "default": 0},
            {"key": "qtd_moeda_01real", "type": "int", "default": 0},
            {"key": "qtd_moeda_02reais", "type": "int", "default": 0},
            {"key": "qtd_moeda_05reais", "type": "int", "default": 0},
            {"key": "qtd_moeda_10reais", "type": "int", "default": 0},
            {"key": "qtd_moeda_20reais", "type": "int", "default": 0},
            {"key": "qtd_moeda_50reais", "type": "int", "default": 0},
            {"key": "qtd_moeda_100reais", "type": "int", "default": 0},
            {"key": "observacoes", "type": None, "default": ""},
        ]

        for item in valores_array:
            try:
                with transaction.atomic():
                    if valid_dict_value(post_data, item["key"]):
                        if item["type"] == "float":
                            value = float(post_data[item["key"]].replace(",", "."))
                        elif item["type"] == "int":
                            value = int(post_data[item["key"]])
                        else:
                            value = post_data[item["key"]]

                        setattr(f_caixa, item["key"], value)

                    f_caixa.save()

            except Exception as error:
                capture_exception(error)
                erro = f"[B001] Houve um erro ao adicionar os registros de valores!\n\t{error}"
                logger.error("::: SALVAR FCAIXA|VALORES FCAIXA|%s", erro)
                break

        logger.info(
            "::: SALVAR FCAIXA|VALORES FCAIXA|Salvos os valores gerais do fechamento de caixa."
        )
        return (f_caixa, erro)
